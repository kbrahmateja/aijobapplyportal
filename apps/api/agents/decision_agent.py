from datetime import datetime, timedelta, timezone
from models import User, SubscriptionTier, Application, Job, Resume
from sqlalchemy.orm import Session
import logging

class ApplicationDecisionAgent:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def decide_and_queue(self, user: User, job_id: int, resume_id: int, match_score: float) -> Application:
        """
        Decides whether to apply immediately, queue for later, or reject based on tier and quota.
        """
        
        # 1. Check if already applied
        existing = self.db.query(Application).filter(
            Application.user_id == user.id,
            Application.job_id == job_id
        ).first()
        
        if existing:
            return existing

        # 2. Check Daily Quota
        # Reset quota if it's a new day (simple logic for MVP, ideally a background job handles this)
        # For now, we just check current counter. 
        # TODO: Implement proper daily reset logic.
        
        if user.quota_used_today >= user.daily_quota:
             # Quota exceeded
             # If FREE -> Reject/Error
             # If PRO/EXPERT -> Queue for tomorrow? Or just Reject for now.
             # MVP Decision: Reject if quota exceeded.
             raise ValueError(f"Daily quota of {user.daily_quota} exceeded for tier {user.subscription_tier}")

        # 3. Decision Logic based on Tier
        status = "queued"
        scheduled_at = datetime.now(timezone.utc)
        reason = "Standard application"

        if user.subscription_tier == SubscriptionTier.FREE:
            # FREE: 
            # - Must be > 80% match
            # - Processed slower (simulated by scheduling 1 hour later)
            if match_score < 0.8:
                status = "rejected"
                reason = f"Match score {match_score:.2f} below Free tier threshold (0.8)"
            else:
                status = "queued"
                scheduled_at = datetime.now(timezone.utc) + timedelta(hours=1)
                reason = "Free tier: Scheduled with 1h delay"

        elif user.subscription_tier == SubscriptionTier.PRO:
            # PRO:
            # - Must be > 60% match
            # - Processed immediately
            if match_score < 0.6:
                status = "rejected"
                reason = f"Match score {match_score:.2f} below Pro tier threshold (0.6)"
            else:
                status = "queued"
                scheduled_at = datetime.now(timezone.utc)
                reason = "Pro tier: Immediate scheduling"

        elif user.subscription_tier == SubscriptionTier.EXPERT:
            # EXPERT:
            # - No threshold (User decides)
            # - Priority queueing (e.g. -5 min to jump queue)
            status = "queued"
            scheduled_at = datetime.now(timezone.utc) - timedelta(minutes=5) 
            reason = "Expert tier: Priority scheduling"

        # 4. Create Application Record
        application = Application(
            user_id=user.id,
            job_id=job_id,
            resume_id=resume_id,
            status=status,
            match_score=match_score,
            scheduled_at=scheduled_at,
            decision_reason=reason,
            applied_at=None # Will be set when actually executed
        )
        
        if status != "rejected":
             user.quota_used_today += 1
        
        self.db.add(application)
        self.db.add(user) # Update quota
        self.db.commit()
        self.db.refresh(application)
        
        return application
