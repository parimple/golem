"""
Predictive Scaling System - Scales before you need it
Inspired by Tesla's predictive maintenance and Apple's seamless performance
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import numpy as np
from collections import deque
import aiohttp
import json

logger = logging.getLogger(__name__)


@dataclass
class LoadPrediction:
    """A prediction about future load"""
    timestamp: datetime
    predicted_load: float  # 0-1 scale
    confidence: float  # 0-1 scale
    reason: str  # Why we predict this
    recommended_action: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def severity(self) -> str:
        """Categorize prediction severity"""
        if self.predicted_load > 0.9:
            return "critical"
        elif self.predicted_load > 0.7:
            return "high"
        elif self.predicted_load > 0.5:
            return "medium"
        return "low"


@dataclass
class ScalingAction:
    """An action taken to scale resources"""
    timestamp: datetime
    action_type: str  # scale_up, scale_down, optimize
    target: str  # What to scale (workers, cache, etc)
    from_value: Any
    to_value: Any
    prediction: Optional[LoadPrediction] = None
    success: bool = False
    impact: float = 0.0  # Measured impact on performance


class PatternAnalyzer:
    """Analyzes usage patterns to predict future load"""
    
    def __init__(self, history_size: int = 10000):
        self.command_history = deque(maxlen=history_size)
        self.load_history = deque(maxlen=history_size)
        self.patterns = {
            'hourly': {},  # Hour of day patterns
            'daily': {},   # Day of week patterns
            'seasonal': {} # Seasonal patterns
        }
        
    def record_event(self, event_type: str, timestamp: datetime, load: float):
        """Record an event for pattern analysis"""
        self.command_history.append({
            'type': event_type,
            'timestamp': timestamp,
            'load': load,
            'hour': timestamp.hour,
            'weekday': timestamp.weekday(),
            'day': timestamp.day
        })
        
        self.load_history.append((timestamp, load))
        
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze historical patterns"""
        if len(self.command_history) < 100:
            return {}
            
        # Hourly patterns
        hourly_loads = {}
        for event in self.command_history:
            hour = event['hour']
            if hour not in hourly_loads:
                hourly_loads[hour] = []
            hourly_loads[hour].append(event['load'])
            
        self.patterns['hourly'] = {
            hour: np.mean(loads) for hour, loads in hourly_loads.items()
        }
        
        # Daily patterns
        daily_loads = {}
        for event in self.command_history:
            day = event['weekday']
            if day not in daily_loads:
                daily_loads[day] = []
            daily_loads[day].append(event['load'])
            
        self.patterns['daily'] = {
            day: np.mean(loads) for day, loads in daily_loads.items()
        }
        
        return self.patterns
    
    def predict_load(self, target_time: datetime) -> Tuple[float, float]:
        """Predict load at target time (load, confidence)"""
        if not self.patterns['hourly']:
            return 0.5, 0.1  # Low confidence default
            
        # Get base predictions
        hour_load = self.patterns['hourly'].get(target_time.hour, 0.5)
        day_load = self.patterns['daily'].get(target_time.weekday(), 0.5)
        
        # Combine predictions
        predicted_load = (hour_load * 0.6 + day_load * 0.4)
        
        # Calculate confidence based on data amount
        data_points = len(self.command_history)
        confidence = min(0.9, data_points / 1000)
        
        return predicted_load, confidence


class EventPredictor:
    """Predicts load based on external events"""
    
    def __init__(self):
        self.known_events = {
            'game_release': {'impact': 0.8, 'duration': timedelta(days=3)},
            'tournament': {'impact': 0.9, 'duration': timedelta(days=1)},
            'holiday': {'impact': 0.6, 'duration': timedelta(days=1)},
            'maintenance': {'impact': -0.5, 'duration': timedelta(hours=2)}
        }
        
    async def check_upcoming_events(self) -> List[Dict[str, Any]]:
        """Check for upcoming events that might affect load"""
        events = []
        
        # Check game releases (mock - would use real API)
        game_releases = await self._check_game_releases()
        events.extend(game_releases)
        
        # Check holidays
        holidays = self._check_holidays()
        events.extend(holidays)
        
        # Check scheduled maintenance
        maintenance = self._check_maintenance()
        events.extend(maintenance)
        
        return events
    
    async def _check_game_releases(self) -> List[Dict[str, Any]]:
        """Check upcoming game releases"""
        # In production, this would call Steam API, gaming news APIs, etc.
        # For now, return mock data
        upcoming = []
        
        # Simulate checking for major game release
        next_friday = datetime.now()
        days_ahead = 4 - next_friday.weekday()  # Friday is 4
        if days_ahead <= 0:
            days_ahead += 7
        next_friday += timedelta(days=days_ahead)
        
        upcoming.append({
            'type': 'game_release',
            'name': 'Major Game Release',
            'date': next_friday,
            'impact': 0.8,
            'confidence': 0.7
        })
        
        return upcoming
    
    def _check_holidays(self) -> List[Dict[str, Any]]:
        """Check for upcoming holidays"""
        holidays = []
        now = datetime.now()
        
        # Check if weekend is coming
        if now.weekday() >= 3:  # Thursday or later
            days_to_saturday = 5 - now.weekday()
            if days_to_saturday <= 0:
                days_to_saturday += 7
            weekend_start = now + timedelta(days=days_to_saturday)
            
            holidays.append({
                'type': 'holiday',
                'name': 'Weekend',
                'date': weekend_start,
                'impact': 0.6,
                'confidence': 0.9
            })
            
        return holidays
    
    def _check_maintenance(self) -> List[Dict[str, Any]]:
        """Check scheduled maintenance windows"""
        # In production, this would check maintenance calendar
        return []


class SentimentAnalyzer:
    """Analyzes social media sentiment to predict load"""
    
    def __init__(self):
        self.sentiment_cache = {}
        self.trending_topics = []
        
    async def analyze_sentiment(self, keywords: List[str]) -> Dict[str, float]:
        """Analyze social media sentiment for keywords"""
        sentiment_scores = {}
        
        for keyword in keywords:
            # In production, this would call Twitter API, Reddit API, etc.
            # For now, simulate with random sentiment
            sentiment = await self._get_keyword_sentiment(keyword)
            sentiment_scores[keyword] = sentiment
            
        return sentiment_scores
    
    async def _get_keyword_sentiment(self, keyword: str) -> float:
        """Get sentiment score for keyword (0=negative, 1=positive)"""
        # Check cache
        if keyword in self.sentiment_cache:
            cached_time, score = self.sentiment_cache[keyword]
            if datetime.now() - cached_time < timedelta(hours=1):
                return score
                
        # In production: call sentiment analysis API
        # For now: simulate
        score = np.random.uniform(0.3, 0.8)
        self.sentiment_cache[keyword] = (datetime.now(), score)
        
        return score
    
    async def detect_trending(self) -> List[Dict[str, Any]]:
        """Detect trending topics that might affect load"""
        # In production: use Twitter trending API, Reddit hot, etc.
        trending = []
        
        # Simulate finding trending topic
        if np.random.random() > 0.7:  # 30% chance
            trending.append({
                'topic': 'BotFeatureRequest',
                'momentum': np.random.uniform(0.5, 1.0),
                'sentiment': np.random.uniform(0.6, 0.9),
                'predicted_impact': 0.4
            })
            
        self.trending_topics = trending
        return trending


class PredictiveScaler:
    """
    Main predictive scaling system
    Scales resources before load arrives
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.pattern_analyzer = PatternAnalyzer()
        self.event_predictor = EventPredictor()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Scaling history
        self.predictions: List[LoadPrediction] = []
        self.actions: List[ScalingAction] = []
        
        # Current scaling state
        self.current_scale = {
            'workers': 4,
            'cache_size': 1000,
            'rate_limit': 100,
            'prefetch_enabled': False
        }
        
        # Scaling limits
        self.scale_limits = {
            'workers': (2, 32),
            'cache_size': (100, 10000),
            'rate_limit': (10, 1000)
        }
        
    async def start_prediction_loop(self):
        """Start continuous prediction and scaling loop"""
        while True:
            try:
                # Make predictions
                predictions = await self.predict_future_load()
                
                # Take scaling actions
                for prediction in predictions:
                    if prediction.severity in ['high', 'critical']:
                        await self.execute_scaling(prediction)
                        
                # Wait before next prediction
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Prediction loop error: {e}")
                await asyncio.sleep(600)  # 10 minutes on error
    
    async def predict_future_load(self) -> List[LoadPrediction]:
        """Predict load for next 24 hours"""
        predictions = []
        now = datetime.now()
        
        # Predict hourly for next 24 hours
        for hours_ahead in [1, 2, 4, 8, 12, 24]:
            target_time = now + timedelta(hours=hours_ahead)
            
            # Pattern-based prediction
            pattern_load, pattern_conf = self.pattern_analyzer.predict_load(target_time)
            
            # Event-based prediction
            events = await self.event_predictor.check_upcoming_events()
            event_load = self._calculate_event_impact(events, target_time)
            
            # Sentiment-based prediction
            sentiment = await self._predict_sentiment_impact()
            
            # Combine predictions
            total_load = (
                pattern_load * 0.5 +
                event_load * 0.3 +
                sentiment * 0.2
            )
            
            confidence = pattern_conf * 0.7  # Reduce confidence for combined prediction
            
            # Create prediction
            prediction = LoadPrediction(
                timestamp=target_time,
                predicted_load=min(1.0, total_load),
                confidence=confidence,
                reason=self._generate_prediction_reason(pattern_load, event_load, sentiment),
                recommended_action=self._recommend_action(total_load)
            )
            
            predictions.append(prediction)
            self.predictions.append(prediction)
            
        return predictions
    
    def _calculate_event_impact(self, events: List[Dict], target_time: datetime) -> float:
        """Calculate load impact from events"""
        total_impact = 0.0
        
        for event in events:
            event_time = event['date']
            if abs((event_time - target_time).total_seconds()) < 86400:  # Within 24h
                total_impact += event['impact'] * event['confidence']
                
        return min(1.0, total_impact)
    
    async def _predict_sentiment_impact(self) -> float:
        """Predict load impact from social sentiment"""
        # Analyze sentiment for bot-related keywords
        keywords = ['discord bot', 'golem bot', self.bot.user.name if self.bot.user else 'bot']
        sentiment_scores = await self.sentiment_analyzer.analyze_sentiment(keywords)
        
        # Detect trending topics
        trending = await self.sentiment_analyzer.detect_trending()
        
        # Calculate impact
        base_impact = np.mean(list(sentiment_scores.values()))
        trending_impact = sum(t['predicted_impact'] for t in trending)
        
        return min(1.0, base_impact + trending_impact)
    
    def _generate_prediction_reason(self, pattern: float, event: float, sentiment: float) -> str:
        """Generate human-readable prediction reason"""
        reasons = []
        
        if pattern > 0.7:
            reasons.append("Historical patterns show high load")
        elif pattern > 0.5:
            reasons.append("Moderate load expected based on patterns")
            
        if event > 0.5:
            reasons.append("Upcoming events detected")
            
        if sentiment > 0.7:
            reasons.append("High social media activity")
            
        return "; ".join(reasons) if reasons else "Normal load expected"
    
    def _recommend_action(self, predicted_load: float) -> str:
        """Recommend scaling action based on load"""
        if predicted_load > 0.9:
            return "Maximum scale-up recommended"
        elif predicted_load > 0.7:
            return "Moderate scale-up recommended"
        elif predicted_load > 0.5:
            return "Monitor closely, prepare to scale"
        elif predicted_load < 0.3:
            return "Consider scaling down"
        return "Maintain current scale"
    
    async def execute_scaling(self, prediction: LoadPrediction):
        """Execute scaling based on prediction"""
        logger.info(f"Executing scaling for prediction: {prediction.reason}")
        
        if prediction.predicted_load > 0.8:
            # Scale up
            await self.scale_up(prediction)
        elif prediction.predicted_load < 0.3:
            # Scale down
            await self.scale_down(prediction)
        else:
            # Optimize current resources
            await self.optimize_resources(prediction)
    
    async def scale_up(self, prediction: LoadPrediction):
        """Scale up resources"""
        actions = []
        
        # Increase workers
        old_workers = self.current_scale['workers']
        new_workers = min(
            self.scale_limits['workers'][1],
            int(old_workers * 1.5)
        )
        if new_workers > old_workers:
            self.current_scale['workers'] = new_workers
            actions.append(ScalingAction(
                timestamp=datetime.now(),
                action_type='scale_up',
                target='workers',
                from_value=old_workers,
                to_value=new_workers,
                prediction=prediction
            ))
            
        # Increase cache
        old_cache = self.current_scale['cache_size']
        new_cache = min(
            self.scale_limits['cache_size'][1],
            int(old_cache * 2)
        )
        if new_cache > old_cache:
            self.current_scale['cache_size'] = new_cache
            actions.append(ScalingAction(
                timestamp=datetime.now(),
                action_type='scale_up',
                target='cache_size',
                from_value=old_cache,
                to_value=new_cache,
                prediction=prediction
            ))
            
        # Enable prefetching
        if not self.current_scale['prefetch_enabled']:
            self.current_scale['prefetch_enabled'] = True
            actions.append(ScalingAction(
                timestamp=datetime.now(),
                action_type='scale_up',
                target='prefetch',
                from_value=False,
                to_value=True,
                prediction=prediction
            ))
            
        # Apply actions
        for action in actions:
            await self._apply_scaling_action(action)
            self.actions.append(action)
            
        logger.info(f"Scaled up: {len(actions)} actions taken")
    
    async def scale_down(self, prediction: LoadPrediction):
        """Scale down resources to save costs"""
        actions = []
        
        # Reduce workers
        old_workers = self.current_scale['workers']
        new_workers = max(
            self.scale_limits['workers'][0],
            int(old_workers * 0.7)
        )
        if new_workers < old_workers:
            self.current_scale['workers'] = new_workers
            actions.append(ScalingAction(
                timestamp=datetime.now(),
                action_type='scale_down',
                target='workers',
                from_value=old_workers,
                to_value=new_workers,
                prediction=prediction
            ))
            
        # Apply actions
        for action in actions:
            await self._apply_scaling_action(action)
            self.actions.append(action)
            
        logger.info(f"Scaled down: {len(actions)} actions taken")
    
    async def optimize_resources(self, prediction: LoadPrediction):
        """Optimize current resources without scaling"""
        # Future: implement resource optimization
        pass
    
    async def _apply_scaling_action(self, action: ScalingAction):
        """Apply a scaling action to the system"""
        try:
            if action.target == 'workers':
                # In production: adjust worker pool size
                logger.info(f"Adjusted workers: {action.from_value} → {action.to_value}")
                
            elif action.target == 'cache_size':
                # In production: adjust cache size
                logger.info(f"Adjusted cache: {action.from_value} → {action.to_value}")
                
            elif action.target == 'prefetch':
                # In production: enable/disable prefetching
                logger.info(f"Prefetching: {action.to_value}")
                
            action.success = True
            
        except Exception as e:
            logger.error(f"Failed to apply scaling action: {e}")
            action.success = False
    
    def get_scaling_status(self) -> Dict[str, Any]:
        """Get current scaling status"""
        recent_predictions = self.predictions[-10:] if self.predictions else []
        recent_actions = self.actions[-10:] if self.actions else []
        
        return {
            'current_scale': self.current_scale,
            'recent_predictions': [
                {
                    'time': p.timestamp.isoformat(),
                    'load': p.predicted_load,
                    'confidence': p.confidence,
                    'severity': p.severity
                }
                for p in recent_predictions
            ],
            'recent_actions': [
                {
                    'time': a.timestamp.isoformat(),
                    'type': a.action_type,
                    'target': a.target,
                    'change': f"{a.from_value} → {a.to_value}"
                }
                for a in recent_actions
            ],
            'patterns': self.pattern_analyzer.patterns
        }