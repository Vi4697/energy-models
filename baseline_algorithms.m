function baseline_algorithms()
    % BASELINE_ALGORITHMS - Implementation of standard task scheduling algorithms for comparison
    %
    % This module implements 5 baseline scheduling algorithms to compare against
    % our intelligent prioritization approach:
    %
    % 1. FIFO (First-In-First-Out) - Traditional sequential execution
    % 2. Energy-Greedy - Execute lowest energy tasks first  
    % 3. Urgency-First - Execute most urgent tasks first
    % 4. Random - Random task ordering
    % 5. WSPT (Weighted Shortest Processing Time) - Industry standard
    %
    % These baselines establish proper scientific comparison for research validation.
    
    fprintf('=== BASELINE ALGORITHM COMPARISON SUITE ===\n\n');
    
    % Test all algorithms on the same scenario
    testScenario = generateComparisonScenario();
    
    algorithms = {
        {'FIFO', @fifoScheduler};
        {'Energy-Greedy', @energyGreedyScheduler};
        {'Urgency-First', @urgencyFirstScheduler};
        {'Random', @randomScheduler};
        {'WSPT', @wsptScheduler};
        {'Our Prioritization', @ourPrioritizationScheduler};
    };
    
    results = struct();
    
    fprintf('Running comparison with %d tasks under %.1f%% energy constraint...\n\n', ...
            length(testScenario.tasks), testScenario.energyLevel * 100);
    
    for i = 1:length(algorithms)
        algorithmName = algorithms{i}{1};
        algorithmFunc = algorithms{i}{2};
        
        fprintf('Testing %s...\n', algorithmName);
        
        try
            result = runAlgorithmTest(algorithmFunc, testScenario);
            results.(matlab.lang.makeValidName(algorithmName)) = result;
            
            fprintf('  Tasks completed: %d/%d (%.1f%%)\n', result.tasksCompleted, ...
                    result.totalTasks, result.completionRate);
            fprintf('  Energy used: %.3f kWh\n', result.energyUsed);
            fprintf('  Total reward: %.1f points\n', result.totalReward);
            fprintf('  Efficiency: %.1f reward/kWh\n', result.efficiency);
            
        catch ME
            fprintf('  ERROR: %s\n', ME.message);
            results.(matlab.lang.makeValidName(algorithmName)) = struct('error', ME.message);
        end
        
        fprintf('\n');
    end
    
    % Generate comparison report
    generateComparisonReport(results);
    
    % Save results for further analysis
    save('baseline_comparison_results.mat', 'results', 'testScenario');
    
    fprintf('Baseline comparison complete. Results saved to baseline_comparison_results.mat\n');
end

function scenario = generateComparisonScenario()
    % Generate a standard scenario for algorithm comparison
    scenario = struct();
    scenario.energyLevel = 0.4; % 40% energy constraint - forces difficult choices
    
    % Standard task set with varied characteristics for meaningful comparison
    scenario.tasks = {
        % {typeIndex, duration, urgency, reward, description}
        struct('typeIndex', 6, 'duration', 0.2, 'urgency', 9, 'reward', 15, 'description', 'Critical communication');
        struct('typeIndex', 3, 'duration', 4.0, 'urgency', 2, 'reward', 8, 'description', 'Low-priority drilling');
        struct('typeIndex', 4, 'duration', 0.5, 'urgency', 7, 'reward', 12, 'description', 'Important imaging');
        struct('typeIndex', 5, 'duration', 1.5, 'urgency', 5, 'reward', 10, 'description', 'Standard analysis');
        struct('typeIndex', 2, 'duration', 2.0, 'urgency', 8, 'reward', 18, 'description', 'High-value sampling');
        struct('typeIndex', 1, 'duration', 0.1, 'urgency', 10, 'reward', 6, 'description', 'Emergency navigation');
        struct('typeIndex', 3, 'duration', 3.0, 'urgency', 3, 'reward', 12, 'description', 'Optional drilling');
        struct('typeIndex', 4, 'duration', 0.8, 'urgency', 6, 'reward', 8, 'description', 'Documentation');
        struct('typeIndex', 5, 'duration', 2.2, 'urgency', 4, 'reward', 14, 'description', 'Extended analysis');
        struct('typeIndex', 2, 'duration', 1.2, 'urgency', 7, 'reward', 16, 'description', 'Target sampling');
    };
    
    % Add computed fields for convenience
    powerMap = containers.Map([1, 2, 3, 4, 5, 6], [50, 80, 120, 30, 45, 25]);
    for i = 1:length(scenario.tasks)
        task = scenario.tasks{i};
        task.power = powerMap(task.typeIndex);
        task.energy = task.power * task.duration / 1000; % Convert to kWh
        task.id = sprintf('T%03d', i);
        scenario.tasks{i} = task;
    end
end

function result = runAlgorithmTest(algorithmFunc, scenario)
    % Run a single algorithm test and return standardized results
    
    % Get task ordering from algorithm
    orderedTasks = algorithmFunc(scenario.tasks);
    
    % Simulate execution with energy constraints
    executionResult = simulateTaskExecution(orderedTasks, scenario.energyLevel);
    
    % Package results in standard format
    result = struct();
    result.totalTasks = length(scenario.tasks);
    result.tasksCompleted = length(executionResult.completedTasks);
    result.completionRate = result.tasksCompleted / result.totalTasks * 100;
    result.energyUsed = executionResult.totalEnergy;
    result.totalReward = executionResult.totalReward;
    result.executionTime = executionResult.totalTime;
    result.efficiency = result.totalReward / max(result.energyUsed, 0.001); % Avoid division by zero
    result.taskOrder = {executionResult.completedTasks.id};
    result.skippedTasks = {executionResult.skippedTasks.id};
end

function executionResult = simulateTaskExecution(orderedTasks, energyLevel)
    % Simulate task execution under energy constraints
    
    % Rover parameters (simplified)
    batteryCapacity = 42.24; % kWh
    terrainEnergy = 0.061; % kWh (typical)
    reserveRatio = 0.20;
    
    % Calculate available energy
    totalEnergy = batteryCapacity * energyLevel;
    availableEnergy = totalEnergy - terrainEnergy;
    reserveEnergy = availableEnergy * reserveRatio;
    usableEnergy = max(0, availableEnergy - reserveEnergy);
    
    % Execute tasks in order
    completedTasks = [];
    skippedTasks = [];
    energyUsed = terrainEnergy;
    totalReward = 0;
    totalTime = 0;
    
    for i = 1:length(orderedTasks)
        task = orderedTasks(i);
        
        if task.energy <= usableEnergy
            % Task can be executed
            completedTasks(end+1) = task;
            usableEnergy = usableEnergy - task.energy;
            energyUsed = energyUsed + task.energy;
            totalReward = totalReward + task.reward;
            totalTime = totalTime + task.duration;
        else
            % Task must be skipped
            skippedTasks(end+1) = task;
        end
    end
    
    executionResult = struct();
    executionResult.completedTasks = completedTasks;
    executionResult.skippedTasks = skippedTasks;
    executionResult.totalEnergy = energyUsed;
    executionResult.totalReward = totalReward;
    executionResult.totalTime = totalTime;
end

% ===== BASELINE ALGORITHM IMPLEMENTATIONS =====

function orderedTasks = fifoScheduler(tasks)
    % FIFO: Execute tasks in original order (no optimization)
    orderedTasks = tasks;
end

function orderedTasks = energyGreedyScheduler(tasks)
    % Energy-Greedy: Execute lowest energy tasks first
    energies = zeros(length(tasks), 1);
    
    for i = 1:length(tasks)
        energies(i) = tasks{i}.energy;
    end
    
    [~, sortIdx] = sort(energies);
    orderedTasks = tasks(sortIdx);
end

function orderedTasks = urgencyFirstScheduler(tasks)
    % Urgency-First: Execute most urgent tasks first
    urgencies = zeros(length(tasks), 1);
    
    for i = 1:length(tasks)
        urgencies(i) = tasks{i}.urgency;
    end
    
    [~, sortIdx] = sort(urgencies, 'descend'); % High urgency first
    orderedTasks = tasks(sortIdx);
end

function orderedTasks = randomScheduler(tasks)
    % Random: Execute tasks in random order
    randomOrder = randperm(length(tasks));
    orderedTasks = tasks(randomOrder);
end

function orderedTasks = wsptScheduler(tasks)
    % WSPT: Weighted Shortest Processing Time (industry standard)
    % Priority = Reward / Duration (higher is better)
    
    priorities = zeros(length(tasks), 1);
    
    for i = 1:length(tasks)
        priorities(i) = tasks{i}.reward / max(tasks{i}.duration, 0.01); % Avoid division by zero
    end
    
    [~, sortIdx] = sort(priorities, 'descend'); % High priority first
    orderedTasks = tasks(sortIdx);
end

function orderedTasks = ourPrioritizationScheduler(tasks)
    % Our Algorithm: Multi-criteria prioritization with energy efficiency
    
    priorities = zeros(length(tasks), 1);
    
    % Algorithm parameters
    lambda1 = 1.0;   % Energy cost weight
    lambda2 = 0.5;   % Urgency weight  
    lambda3 = -2.0;  % Reward weight (negative to maximize)
    
    for i = 1:length(tasks)
        task = tasks{i};
        
        % Enhanced priority calculation
        energyCost = lambda1 * task.energy;
        urgencyFactor = lambda2 * (1.0 / max(task.urgency, 0.1));
        rewardFactor = lambda3 * task.reward;
        
        % Energy efficiency bonus
        energyEfficiency = task.reward / max(task.energy, 0.001);
        efficiencyBonus = -0.5 * energyEfficiency;
        
        % Time sensitivity bonus
        timeSensitivityBonus = 0;
        if task.urgency > 8.0
            timeSensitivityBonus = -1.0; % High urgency bonus
        elseif task.urgency < 3.0
            timeSensitivityBonus = 0.5;  % Low urgency penalty
        end
        
        priorities(i) = energyCost + urgencyFactor + rewardFactor + efficiencyBonus + timeSensitivityBonus;
    end
    
    [~, sortIdx] = sort(priorities); % Lower priority value = higher actual priority
    orderedTasks = tasks(sortIdx);
end

function generateComparisonReport(results)
    % Generate comprehensive comparison report
    
    fprintf('=== ALGORITHM COMPARISON REPORT ===\n\n');
    
    % Extract metrics from results
    algorithms = fieldnames(results);
    metrics = {'completionRate', 'energyUsed', 'totalReward', 'efficiency'};
    
    % Create comparison table
    fprintf('%-20s %15s %15s %15s %15s\n', 'Algorithm', 'Completion %', 'Energy kWh', 'Total Reward', 'Efficiency');
    fprintf('%s\n', repmat('-', 1, 80));
    
    for i = 1:length(algorithms)
        alg = algorithms{i};
        
        if isfield(results.(alg), 'error')
            fprintf('%-20s %15s %15s %15s %15s\n', alg, 'ERROR', 'ERROR', 'ERROR', 'ERROR');
        else
            r = results.(alg);
            fprintf('%-20s %15.1f %15.3f %15.1f %15.1f\n', ...
                    alg, r.completionRate, r.energyUsed, r.totalReward, r.efficiency);
        end
    end
    
    fprintf('\n');
    
    % Find best performer in each category
    validResults = struct();
    validAlgorithms = {};
    
    for i = 1:length(algorithms)
        alg = algorithms{i};
        if ~isfield(results.(alg), 'error')
            validResults.(alg) = results.(alg);
            validAlgorithms{end+1} = alg;
        end
    end
    
    if ~isempty(validAlgorithms)
        fprintf('BEST PERFORMERS:\n');
        
        % Best completion rate
        bestCompletion = '';
        maxCompletion = 0;
        for i = 1:length(validAlgorithms)
            alg = validAlgorithms{i};
            if validResults.(alg).completionRate > maxCompletion
                maxCompletion = validResults.(alg).completionRate;
                bestCompletion = alg;
            end
        end
        fprintf('• Highest Completion Rate: %s (%.1f%%)\n', bestCompletion, maxCompletion);
        
        % Best efficiency
        bestEfficiency = '';
        maxEfficiency = 0;
        for i = 1:length(validAlgorithms)
            alg = validAlgorithms{i};
            if validResults.(alg).efficiency > maxEfficiency
                maxEfficiency = validResults.(alg).efficiency;
                bestEfficiency = alg;
            end
        end
        fprintf('• Highest Efficiency: %s (%.1f reward/kWh)\n', bestEfficiency, maxEfficiency);
        
        % Best total reward
        bestReward = '';
        maxReward = 0;
        for i = 1:length(validAlgorithms)
            alg = validAlgorithms{i};
            if validResults.(alg).totalReward > maxReward
                maxReward = validResults.(alg).totalReward;
                bestReward = alg;
            end
        end
        fprintf('• Highest Total Reward: %s (%.1f points)\n', bestReward, maxReward);
        
        % Calculate improvements over FIFO
        if isfield(validResults, 'FIFO')
            fifoResult = validResults.FIFO;
            fprintf('\nIMPROVEMENT OVER FIFO:\n');
            
            for i = 1:length(validAlgorithms)
                alg = validAlgorithms{i};
                if ~strcmp(alg, 'FIFO')
                    r = validResults.(alg);
                    completionImprovement = r.completionRate - fifoResult.completionRate;
                    efficiencyImprovement = ((r.efficiency - fifoResult.efficiency) / max(fifoResult.efficiency, 0.1)) * 100;
                    rewardImprovement = r.totalReward - fifoResult.totalReward;
                    
                    fprintf('• %s: +%.1f%% completion, +%.1f%% efficiency, +%.1f reward\n', ...
                            alg, completionImprovement, efficiencyImprovement, rewardImprovement);
                end
            end
        end
    end
    
    fprintf('\n');
end

% Main execution function for standalone testing
if nargin == 0 && nargout == 0
    baseline_algorithms();
end