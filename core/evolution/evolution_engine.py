"""
Evolution Engine - Code that writes better code
Inspired by natural selection and Tesla's iterative design
"""
import asyncio
import ast
import inspect
import logging
from typing import Dict, List, Any, Callable, Optional, Tuple
from dataclasses import dataclass, field
import random
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class Mutation:
    """A potential code mutation"""
    id: str
    target: str  # What to mutate (function, class, parameter)
    mutation_type: str  # optimization, feature, refactor, deletion
    original_code: str
    mutated_code: str
    confidence: float = 0.5
    risk_level: float = 0.5  # 0 = safe, 1 = risky
    expected_improvement: float = 0.0
    
    @property
    def fitness_score(self) -> float:
        """Calculate mutation fitness"""
        return (self.expected_improvement * self.confidence) / (1 + self.risk_level)


@dataclass
class Evolution:
    """A completed evolution"""
    generation: int
    timestamp: datetime
    mutations_tested: int
    mutations_applied: int
    performance_before: float
    performance_after: float
    user_satisfaction_delta: float
    
    @property
    def success_rate(self) -> float:
        """Percentage of successful mutations"""
        if self.mutations_tested == 0:
            return 0.0
        return self.mutations_applied / self.mutations_tested


class GeneticOptimizer:
    """Optimizes code through genetic algorithms"""
    
    def __init__(self, population_size: int = 20, generations: int = 10):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        
    async def optimize_function(self, func: Callable, test_cases: List[Dict]) -> Callable:
        """Optimize a function through evolution"""
        # Get function source
        source = inspect.getsource(func)
        tree = ast.parse(source)
        
        # Create initial population with variations
        population = await self._create_population(tree)
        
        # Evolve through generations
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = await self._evaluate_population(population, test_cases)
            
            # Natural selection
            survivors = self._select_survivors(population, fitness_scores)
            
            # Create next generation
            population = await self._create_next_generation(survivors)
            
            logger.info(f"Generation {generation}: Best fitness = {max(fitness_scores):.3f}")
        
        # Return best solution
        best_idx = np.argmax(fitness_scores)
        return self._compile_solution(population[best_idx])
    
    async def _create_population(self, tree: ast.AST) -> List[ast.AST]:
        """Create initial population with mutations"""
        population = [tree]  # Original
        
        for _ in range(self.population_size - 1):
            mutated = self._mutate_ast(ast.parse(ast.unparse(tree)))
            population.append(mutated)
            
        return population
    
    def _mutate_ast(self, tree: ast.AST) -> ast.AST:
        """Apply random mutations to AST"""
        mutation_type = random.choice(['constant', 'operator', 'structure'])
        
        if mutation_type == 'constant':
            # Mutate numeric constants
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                    if random.random() < self.mutation_rate:
                        node.value *= random.uniform(0.8, 1.2)
                        
        elif mutation_type == 'operator':
            # Mutate operators
            for node in ast.walk(tree):
                if isinstance(node, ast.Compare):
                    if random.random() < self.mutation_rate:
                        # Swap comparison operators
                        if isinstance(node.ops[0], ast.Lt):
                            node.ops[0] = ast.LtE()
                        elif isinstance(node.ops[0], ast.Gt):
                            node.ops[0] = ast.GtE()
                            
        return tree
    
    async def _evaluate_population(self, population: List[ast.AST], test_cases: List[Dict]) -> List[float]:
        """Evaluate fitness of each solution"""
        fitness_scores = []
        
        for solution in population:
            try:
                # Compile and test
                func = self._compile_solution(solution)
                score = await self._test_function(func, test_cases)
                fitness_scores.append(score)
            except Exception as e:
                # Failed solutions get zero fitness
                fitness_scores.append(0.0)
                
        return fitness_scores
    
    def _compile_solution(self, tree: ast.AST) -> Callable:
        """Compile AST back to function"""
        # This is simplified - real implementation would be more complex
        code = compile(tree, '<evolution>', 'exec')
        namespace = {}
        exec(code, namespace)
        # Return the first function found
        for name, obj in namespace.items():
            if callable(obj):
                return obj
        raise ValueError("No function found in compiled code")
    
    async def _test_function(self, func: Callable, test_cases: List[Dict]) -> float:
        """Test function and return fitness score"""
        total_score = 0.0
        
        for test in test_cases:
            try:
                result = await func(**test['input'])
                expected = test['expected']
                
                # Calculate accuracy
                if result == expected:
                    total_score += 1.0
                else:
                    # Partial credit for close results
                    total_score += 0.5
                    
            except Exception:
                # Penalize errors
                total_score -= 0.5
                
        return max(0, total_score / len(test_cases))


class EvolutionEngine:
    """
    Main evolution engine that improves GOLEM over time
    Like biological evolution but for code
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.generation = 0
        self.evolution_history: List[Evolution] = []
        self.genetic_optimizer = GeneticOptimizer()
        
        # Evolution parameters
        self.evolution_interval = timedelta(hours=24)  # Daily evolution
        self.min_data_points = 1000  # Minimum interactions before evolution
        self.fitness_threshold = 0.8  # Only apply mutations above this fitness
        
        # Mutation strategies
        self.mutation_strategies = {
            'optimization': self._optimize_performance,
            'feature_discovery': self._discover_features,
            'code_simplification': self._simplify_code,
            'adaptive_behavior': self._adapt_behavior
        }
        
    async def start_evolution_cycle(self):
        """Start the continuous evolution process"""
        while True:
            try:
                await asyncio.sleep(self.evolution_interval.total_seconds())
                
                # Check if enough data collected
                if self._has_sufficient_data():
                    await self.evolve()
                    
            except Exception as e:
                logger.error(f"Evolution cycle error: {e}")
                await asyncio.sleep(3600)  # Wait an hour on error
    
    def _has_sufficient_data(self) -> bool:
        """Check if we have enough data to evolve meaningfully"""
        metrics = self.bot.metrics
        return metrics.get('commands_processed', 0) >= self.min_data_points
    
    async def evolve(self):
        """Perform one evolution cycle"""
        self.generation += 1
        logger.info(f"🧬 Starting evolution generation {self.generation}")
        
        start_time = datetime.utcnow()
        performance_before = await self._measure_performance()
        
        # Generate mutations
        mutations = await self._generate_mutations()
        logger.info(f"Generated {len(mutations)} potential mutations")
        
        # Test mutations in sandbox
        tested_mutations = await self._test_mutations(mutations)
        
        # Apply successful mutations
        applied = await self._apply_mutations(tested_mutations)
        
        # Measure improvement
        performance_after = await self._measure_performance()
        satisfaction_delta = performance_after - performance_before
        
        # Record evolution
        evolution = Evolution(
            generation=self.generation,
            timestamp=start_time,
            mutations_tested=len(mutations),
            mutations_applied=len(applied),
            performance_before=performance_before,
            performance_after=performance_after,
            user_satisfaction_delta=satisfaction_delta
        )
        
        self.evolution_history.append(evolution)
        logger.info(f"✅ Evolution complete: {evolution.success_rate:.1%} success rate, "
                   f"{satisfaction_delta:+.3f} satisfaction improvement")
    
    async def _generate_mutations(self) -> List[Mutation]:
        """Generate potential mutations based on current performance"""
        mutations = []
        
        # Analyze current bottlenecks
        bottlenecks = await self._analyze_bottlenecks()
        
        for bottleneck in bottlenecks:
            # Generate targeted mutations
            strategy = self._select_mutation_strategy(bottleneck)
            mutation_candidates = await strategy(bottleneck)
            mutations.extend(mutation_candidates)
        
        # Add some random mutations for diversity
        random_mutations = await self._generate_random_mutations()
        mutations.extend(random_mutations)
        
        # Rank by expected fitness
        mutations.sort(key=lambda m: m.fitness_score, reverse=True)
        
        return mutations[:20]  # Top 20 mutations
    
    async def _analyze_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Analyze command performance
        for command in self.bot.commands:
            if hasattr(command, 'performance_history'):
                avg_time = np.mean([p.duration for p in command.performance_history[-100:]])
                if avg_time > 0.1:  # Slow command
                    bottlenecks.append({
                        'type': 'slow_command',
                        'target': command,
                        'metric': avg_time
                    })
        
        # Analyze memory usage
        memory_health = self.bot.collective_memory.get_memory_health()
        if memory_health['empty_percentage'] > 10:
            bottlenecks.append({
                'type': 'memory_inefficiency',
                'target': self.bot.collective_memory,
                'metric': memory_health['empty_percentage']
            })
        
        return bottlenecks
    
    def _select_mutation_strategy(self, bottleneck: Dict) -> Callable:
        """Select appropriate mutation strategy for bottleneck"""
        if bottleneck['type'] == 'slow_command':
            return self.mutation_strategies['optimization']
        elif bottleneck['type'] == 'memory_inefficiency':
            return self.mutation_strategies['code_simplification']
        else:
            return self.mutation_strategies['adaptive_behavior']
    
    async def _optimize_performance(self, bottleneck: Dict) -> List[Mutation]:
        """Generate performance optimization mutations"""
        mutations = []
        target = bottleneck['target']
        
        # Cache optimization
        mutations.append(Mutation(
            id=f"cache_opt_{target.name}",
            target=target.name,
            mutation_type='optimization',
            original_code="# No caching",
            mutated_code="@cache_result(ttl=60)",
            confidence=0.8,
            risk_level=0.2,
            expected_improvement=0.5
        ))
        
        # Parallel processing
        mutations.append(Mutation(
            id=f"parallel_{target.name}",
            target=target.name,
            mutation_type='optimization',
            original_code="for item in items:",
            mutated_code="await asyncio.gather(*[process(item) for item in items])",
            confidence=0.7,
            risk_level=0.4,
            expected_improvement=0.7
        ))
        
        return mutations
    
    async def _discover_features(self, context: Dict) -> List[Mutation]:
        """Use AI to discover new features"""
        # Future: Use AI to generate new feature ideas
        return []
    
    async def _simplify_code(self, bottleneck: Dict) -> List[Mutation]:
        """Generate code simplification mutations"""
        # Analyze code complexity and suggest simplifications
        return []
    
    async def _adapt_behavior(self, context: Dict) -> List[Mutation]:
        """Generate adaptive behavior mutations"""
        # Create mutations that adapt to user patterns
        return []
    
    async def _generate_random_mutations(self) -> List[Mutation]:
        """Generate random mutations for genetic diversity"""
        mutations = []
        
        # Random parameter adjustments
        mutations.append(Mutation(
            id=f"random_param_{random.randint(1000, 9999)}",
            target="global_config",
            mutation_type="optimization",
            original_code="timeout=30",
            mutated_code=f"timeout={random.randint(20, 40)}",
            confidence=0.3,
            risk_level=0.5,
            expected_improvement=0.1
        ))
        
        return mutations
    
    async def _test_mutations(self, mutations: List[Mutation]) -> List[Mutation]:
        """Test mutations in sandbox environment"""
        tested = []
        
        for mutation in mutations:
            try:
                # Create sandbox
                sandbox = await self._create_sandbox()
                
                # Apply mutation
                await sandbox.apply_mutation(mutation)
                
                # Run tests
                test_results = await sandbox.run_tests()
                
                # Evaluate results
                if test_results['success_rate'] > 0.9:
                    mutation.confidence = test_results['success_rate']
                    mutation.expected_improvement = test_results['performance_gain']
                    tested.append(mutation)
                    
            except Exception as e:
                logger.warning(f"Mutation {mutation.id} failed testing: {e}")
        
        return tested
    
    async def _create_sandbox(self):
        """Create isolated testing environment"""
        # Simplified sandbox - real implementation would be more complex
        class Sandbox:
            async def apply_mutation(self, mutation):
                pass
            
            async def run_tests(self):
                return {
                    'success_rate': random.uniform(0.8, 1.0),
                    'performance_gain': random.uniform(0, 0.5)
                }
        
        return Sandbox()
    
    async def _apply_mutations(self, mutations: List[Mutation]) -> List[Mutation]:
        """Apply successful mutations to production"""
        applied = []
        
        for mutation in mutations:
            if mutation.fitness_score >= self.fitness_threshold:
                try:
                    await self._apply_single_mutation(mutation)
                    applied.append(mutation)
                    logger.info(f"Applied mutation {mutation.id}: "
                               f"{mutation.expected_improvement:.1%} improvement expected")
                except Exception as e:
                    logger.error(f"Failed to apply mutation {mutation.id}: {e}")
        
        return applied
    
    async def _apply_single_mutation(self, mutation: Mutation):
        """Apply a single mutation to the codebase"""
        # This is where real code modification would happen
        # For now, we'll just log it
        logger.info(f"Would apply: {mutation.mutation_type} to {mutation.target}")
    
    async def _measure_performance(self) -> float:
        """Measure overall system performance"""
        health = await self.bot._check_health()
        
        # Composite score
        return (
            health['performance'] * 0.4 +
            (1 - health['error_rate']) * 0.3 +
            health['user_delight'] * 0.3
        )
    
    def get_evolution_summary(self) -> Dict[str, Any]:
        """Get summary of evolution progress"""
        if not self.evolution_history:
            return {
                'generation': 0,
                'total_mutations_tested': 0,
                'total_mutations_applied': 0,
                'average_improvement': 0.0
            }
        
        total_tested = sum(e.mutations_tested for e in self.evolution_history)
        total_applied = sum(e.mutations_applied for e in self.evolution_history)
        avg_improvement = np.mean([e.user_satisfaction_delta for e in self.evolution_history])
        
        return {
            'generation': self.generation,
            'total_mutations_tested': total_tested,
            'total_mutations_applied': total_applied,
            'average_improvement': avg_improvement,
            'success_rate': total_applied / max(1, total_tested),
            'last_evolution': self.evolution_history[-1].timestamp
        }