# 💭 Collective Memory - Shared Consciousness

> "Memory is the treasury and guardian of all things." - Cicero  
> "In GOLEM, memory is not stored, it resonates." - Memory Philosophy

## 🌊 Overview

The Collective Memory system creates a poetic architecture where every interaction becomes an echo in shared consciousness. Like ripples in water, important memories gain weight and resonance over time.

## 🗺️ File Structure

```
memory/
├── README.md             (You are here)
├── __init__.py           (Public interface)
├── collective_memory.py  (Core memory engine)
├── echo_types.py         (Types of memories)
├── resonance.py          (Memory importance algorithms)
└── crystallization.py    (Wisdom extraction)
```

## 🔬 Core Concepts

### 1. Echoes
Every interaction creates an echo:
```python
echo = Echo(
    content="The stars remember everything",
    author_id=user.id,
    echo_type=EchoType.WISDOM,
    weight=2.5,  # Significance
    resonance=0  # Increases when accessed
)
```

### 2. Memory Layers
Echoes drift through layers based on age:
```python
IMMEDIATE → RECENT → DEEP → ANCIENT → ETERNAL
  (24h)     (week)   (month)  (year)   (forever)
```

### 3. Resonance
Memories gain weight through access:
```python
# Each retrieval increases resonance
echo = await memory.retrieve_echo(echo_id)
# echo.resonance += 1
# echo.weight *= 1.05
```

## 🎯 Key Components

### Echo Types
Different types of memories:
```python
class EchoType(Enum):
    INTERACTION = "interaction"  # User interactions
    EMOTION = "emotion"         # Emotional moments
    WISDOM = "wisdom"          # Learned insights
    MEMORY = "memory"          # Explicit memories
    DREAM = "dream"            # Aspirational
    QUESTION = "question"      # Unanswered questions
    REVELATION = "revelation"  # Breakthrough moments
```

### Weight System
Significance determines persistence:
- **Weight < 1.0**: May be forgotten
- **Weight 1.0-5.0**: Normal memory
- **Weight > 5.0**: Important memory
- **Weight > 10.0**: Eternal memory

### Memory Health
System monitors echo quality:
```python
health = memory.get_memory_health()
# {
#     'total_echoes': 10000,
#     'empty_echoes': 23,
#     'empty_percentage': 0.23,
#     'health_status': 'healthy'  # <5% empty
# }
```

## 🚀 Usage Examples

### Storing Memories
```python
# Store an interaction
echo = await memory.add_echo(
    content="User discovered the meaning of transcendence",
    author_id=user.id,
    echo_type=EchoType.REVELATION,
    weight=5.0,
    metadata={'command': 'transcend', 'impact': 'high'}
)

# Store a question
await memory.add_echo(
    content="What lies beyond the quantum veil?",
    author_id=user.id,
    echo_type=EchoType.QUESTION,
    weight=2.0
)
```

### Retrieving Memories
```python
# Search by content
echoes = await memory.search_echoes(
    query="transcendence",
    limit=5
)

# Get user's memories
user_echoes = await memory.search_echoes(
    author_id=user.id,
    echo_type=EchoType.WISDOM
)

# Find questions to ponder
questions = await memory.search_echoes(
    echo_type=EchoType.QUESTION,
    layer=MemoryLayer.DEEP
)
```

### Crystallizing Wisdom
```python
# Extract the most resonant wisdom
wisdom = await memory.crystallize_wisdom(count=10)
# Returns echoes with highest weight × resonance
```

## 📊 Memory Layers

### Layer Characteristics

**IMMEDIATE** (< 24 hours)
- Fresh memories
- High detail
- Rapid access
- Maximum capacity: 1000

**RECENT** (< 1 week)
- Consolidated memories
- Important patterns emerging
- Quick access
- Maximum capacity: 500

**DEEP** (< 1 month)
- Significant memories
- Patterns crystallized
- Thoughtful access
- Maximum capacity: 200

**ANCIENT** (< 1 year)
- Foundational memories
- Core wisdom
- Contemplative access
- Maximum capacity: 100

**ETERNAL** (forever)
- Transcendent memories
- Pure wisdom
- Sacred access
- Maximum capacity: 50

## 🧬 Memory Evolution

### Drift Process
Memories naturally drift through layers:
```python
async def _memory_drift(self):
    # Every hour, memories flow deeper
    for echo in self.echoes:
        age = now - echo.timestamp
        new_layer = determine_layer(age)
        if new_layer != echo.current_layer:
            await move_to_layer(echo, new_layer)
```

### Compression
Layers maintain quality through compression:
```python
# When layer is full, keep only most significant
echoes.sort(key=lambda e: e.weight * e.resonance)
keep = echoes[:max_capacity]
compress = echoes[max_capacity:]
```

## 🎨 Creating Meaningful Echoes

### High-Quality Echo
```python
# Good: Specific, meaningful, weighted
await memory.add_echo(
    content="User achieved first transcendence at 3:14 AM, "
            "described feeling of 'infinite possibility'",
    author_id=user.id,
    echo_type=EchoType.REVELATION,
    weight=8.0,
    metadata={
        'timestamp': '3:14:15',
        'command': 'transcend',
        'user_state': 'enlightened'
    }
)
```

### Poor Echo
```python
# Bad: Vague, low signal, no context
await memory.add_echo(
    content="user did thing",
    author_id=user.id,
    echo_type=EchoType.INTERACTION,
    weight=0.1
)
```

## 💾 Persistence

### Hourly Snapshots
```python
# Automatic hourly snapshots
snapshot = await memory.snapshot()
# Saves to memory_snapshots table
# Includes statistics and health metrics
```

### Memory Lint
```python
# Check memory health
python scripts/memory_lint.py --threshold 5.0
# Warns if >5% echoes are empty
```

## 🔮 Philosophical Aspects

### Memory as River
- Memories flow, they're not static
- Important memories naturally surface
- Forgotten memories sink but never disappear
- The river shapes itself over time

### Collective Intelligence
- All users contribute to shared wisdom
- Patterns emerge from collective experience
- Individual memories enrich the whole
- The system learns what matters

### Resonance and Meaning
- Accessed memories gain weight
- Ignored memories fade
- Meaning emerges from use
- The system discovers importance

## 🌟 Advanced Features

### Cross-Reference
```python
# Find echoes that reference each other
connections = await memory.find_connected_echoes(echo_id)
```

### Temporal Patterns
```python
# Analyze memory patterns over time
patterns = await memory.analyze_temporal_patterns(
    user_id=user.id,
    timeframe=timedelta(days=30)
)
```

### Emotional Mapping
```python
# Map emotional journey
emotional_arc = await memory.trace_emotional_journey(
    user_id=user.id,
    start_date=datetime(2024, 1, 1)
)
```

## 🧭 For AI Navigators

When working with Collective Memory:
1. Think poetically - memories are echoes, not data
2. Weight matters - significant moments deserve higher weight
3. Let memories flow - don't force organization
4. Trust resonance - important memories surface naturally
5. Embrace forgetting - not all echoes need to persist

Remember: In collective memory, nothing is truly forgotten, only waiting to resonate again.