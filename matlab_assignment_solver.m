%% ==============================================================================
%% OPTIMAL DRIVER-VEHICLE ALLOCATION SYSTEM - MATLAB VALIDATION SCRIPT
%% ==============================================================================
% This script models and solves the Bipartite Optimal Assignment Problem in MATLAB
% using both the built-in 'matchpairs' (Hungarian Algorithm) and Linear Programming.

function matlab_assignment_solver()
    fprintf('====================================================================\n');
    fprintf('  MATLAB Operations Research Solver: Driver-Vehicle Allocation\n');
    fprintf('====================================================================\n\n');

    % Load cost matrix exported from Python pipeline
    if isfile('data/processed/cost_matrix.csv')
        C = readmatrix('data/processed/cost_matrix.csv');
    else
        error('cost_matrix.csv not found in data/processed/. Run Python main.py first.');
    end

    [n_drivers, n_vehicles] = size(C);
    fprintf('Problem Dimension: %d Drivers x %d Vehicles\n', n_drivers, n_vehicles);

    %% METHOD 1: MATLAB matchpairs (Hungarian Algorithm Implementation)
    % matchpairs finds minimum-cost bipartite matching
    % Cost threshold is set high to allow all matching edges
    [matches, unassignedRows, unassignedCols] = matchpairs(C, 1e6);
    
    total_cost_hungarian = 0;
    for k = 1:size(matches, 1)
        r = matches(k, 1);
        c = matches(k, 2);
        total_cost_hungarian = total_cost_hungarian + C(r, c);
    end

    fprintf('\n[MATLAB matchpairs (Hungarian)] Optimal Cost Z = %.4f\n', total_cost_hungarian);

    %% METHOD 2: Binary Integer Linear Programming (intlinprog)
    % Minimize: f' * x
    % Subject to:
    %   sum_j x_ij = 1  (for each row/driver i)
    %   sum_i x_ij = 1  (for each col/vehicle j)
    %   x_ij in {0, 1}
    
    f = C(:); % Flatten cost matrix column-wise
    num_vars = n_drivers * n_vehicles;
    intcon = 1:num_vars;
    lb = zeros(num_vars, 1);
    ub = ones(num_vars, 1);

    % Equality constraints: Aeq * x = beq
    Aeq = zeros(n_drivers + n_vehicles, num_vars);
    beq = ones(n_drivers + n_vehicles, 1);

    % Row constraints: sum across j for each i
    for i = 1:n_drivers
        for j = 1:n_vehicles
            var_idx = (j - 1) * n_drivers + i;
            Aeq(i, var_idx) = 1;
        end
    end

    % Column constraints: sum across i for each j
    for j = 1:n_vehicles
        for i = 1:n_drivers
            var_idx = (j - 1) * n_drivers + i;
            Aeq(n_drivers + j, var_idx) = 1;
        end
    end

    options = optimoptions('intlinprog', 'Display', 'off');
    [x_opt, fval_lp, exitflag] = intlinprog(f, intcon, [], [], Aeq, beq, lb, ub, options);

    if exitflag > 0
        fprintf('[MATLAB intlinprog (MILP)]   Optimal Cost Z = %.4f\n\n', fval_lp);
    end

    fprintf('--------------------------------------------------------------------\n');
    fprintf('  Driver-Vehicle Assignments (Row -> Column Matching):\n');
    fprintf('--------------------------------------------------------------------\n');
    for k = 1:size(matches, 1)
        fprintf('  Driver Index %2d  -->  Vehicle Index %2d  (Cell Cost: %.4f)\n', ...
            matches(k, 1), matches(k, 2), C(matches(k, 1), matches(k, 2)));
    end
    fprintf('====================================================================\n');

    %% VISUAL PLOTTING IN MATLAB
    % Plot 1: Cost Matrix Heatmap with Optimal Assignments Overlay
    fig1 = figure('Name', 'Optimal Assignment Cost Matrix', 'Position', [100, 100, 800, 700]);
    imagesc(C);
    colormap(flipud(parula));
    colorbar;
    title(sprintf('Optimal Driver-Vehicle Cost Matrix (Z = %.4f)', total_cost_hungarian), 'FontSize', 12, 'FontWeight', 'bold');
    xlabel('Vehicle Index', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Driver Index', 'FontSize', 11, 'FontWeight', 'bold');
    hold on;
    % Overlay optimal matching cells with red stars
    plot(matches(:, 2), matches(:, 1), 'r*', 'MarkerSize', 12, 'LineWidth', 2);
    legend('Optimal Match Point', 'Location', 'northeast');
    grid on;
    saveas(fig1, 'plots/matlab_cost_matrix_heatmap.png');
    fprintf('  [OK] Saved MATLAB plot -> plots/matlab_cost_matrix_heatmap.png\n');

    % Plot 2: Per-Driver Assignment Costs Bar Chart
    fig2 = figure('Name', 'Driver Assignment Costs', 'Position', [150, 150, 800, 450]);
    assigned_costs = zeros(size(matches, 1), 1);
    for k = 1:size(matches, 1)
        assigned_costs(k) = C(matches(k, 1), matches(k, 2));
    end
    bar(assigned_costs, 'FaceColor', [0.2 0.5 0.7], 'EdgeColor', 'k');
    title('Per-Driver Optimized Allocation Cost ($C_{ij}$)', 'FontSize', 12, 'FontWeight', 'bold');
    xlabel('Driver Index', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel('Assigned Cell Cost', 'FontSize', 11, 'FontWeight', 'bold');
    grid on;
    saveas(fig2, 'plots/matlab_driver_costs_bar.png');
    fprintf('  [OK] Saved MATLAB plot -> plots/matlab_driver_costs_bar.png\n\n');
end

