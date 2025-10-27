# Database Migration: Add is_public Field

## Change Required

Add `is_public` field to the Poll model:

```python
# In app/models/polls.py
class Poll(Base):
    __tablename__ = "polls"

    # ... existing fields ...
    is_public = Column(Boolean, default=True, nullable=False)  # Public by default
```

## Schema Updates

```python
# In app/schemas/poll.py
class PollCreate(BaseModel):
    # ... existing fields ...
    is_public: bool = Field(
        True,
        description="Whether the poll is visible to all users (public) or only accessible via direct link/owner (private)"
    )

class PollRead(BaseModel):
    # ... existing fields ...
    is_public: bool

class PollUpdate(BaseModel):
    # ... existing fields ...
    is_public: Optional[bool] = None
```

## Migration SQL

```sql
-- Add the new column with default value
ALTER TABLE polls ADD COLUMN is_public BOOLEAN DEFAULT TRUE NOT NULL;
```
