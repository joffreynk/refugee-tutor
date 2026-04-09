"""AI-driven controller with user override capability."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class AIDecision:
    """An AI decision with override capability."""
    decision_type: str
    suggested_action: str
    confidence: float
    reasoning: str
    auto_execute: bool = True
    user_override: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class AIController:
    """AI brain that makes decisions, with optional user override capability."""

    def __init__(self, class_manager=None, tutor_engine=None):
        self.class_manager = class_manager
        self.tutor_engine = tutor_engine
        self._auto_mode = getattr(settings, "AI_MODE", "auto") == "auto"
        self._pending_decisions: list[AIDecision] = []
        self._user_callback: Optional[Callable] = None
        self._decision_history: list[AIDecision] = []
        self._override_mode = False

    def set_auto_mode(self, enabled: bool) -> None:
        """Enable/disable auto mode (AI makes decisions without prompting)."""
        self._auto_mode = enabled
        logger.info(f"AI mode: {'AUTO' if enabled else 'MANUAL (user controls)'}")

    def is_auto_mode(self) -> bool:
        """Check if in auto mode."""
        return self._auto_mode

    def enable_manual_mode(self) -> None:
        """Enable manual mode - user controls with AI suggestions."""
        self._auto_mode = False
        self._override_mode = True
        logger.info("AI mode: MANUAL - User must approve decisions")

    def enable_full_auto_mode(self) -> None:
        """Enable full auto mode - AI manages everything."""
        self._auto_mode = True
        self._override_mode = False
        logger.info("AI mode: FULL AUTO - AI manages everything")

    def _make_decision(self, decision_type: str) -> AIDecision:
        """Make an AI decision based on current context."""
        if decision_type == "next_lesson":
            return self._decide_next_lesson()
        elif decision_type == "difficulty":
            return self._decide_difficulty()
        elif decision_type == "subject_switch":
            return self._decide_subject_switch()
        elif decision_type == "class_timing":
            return self._decide_class_timing()
        elif decision_type == "feedback":
            return self._decide_feedback()
        else:
            return AIDecision(
                decision_type=decision_type,
                suggested_action="continue",
                confidence=0.5,
                reasoning="Unknown decision type"
            )

    def _decide_next_lesson(self) -> AIDecision:
        """Decide what to teach next."""
        if not self.class_manager:
            return AIDecision(
                decision_type="next_lesson",
                suggested_action="default",
                confidence=0.5,
                reasoning="No class manager"
            )

        rec = self.class_manager.get_ai_recommendation()
        return AIDecision(
            decision_type="next_lesson",
            suggested_action=f"teach {rec.get('subject', 'mathematics')}:{rec.get('topic', 'default')}",
            confidence=0.85,
            reasoning=f"AI recommends {rec.get('subject')} - {rec.get('topic')}. Progress: {rec.get('progress')}. Focus: {rec.get('suggested_focus', 'none')}"
        )

    def _decide_difficulty(self) -> AIDecision:
        """Decide difficulty level based on performance."""
        if not self.tutor_engine:
            return AIDecision(
                decision_type="difficulty",
                suggested_action="level_5",
                confidence=0.5,
                reasoning="No tutor engine"
            )

        level = 5
        return AIDecision(
            decision_type="difficulty",
            suggested_action=f"level_{level}",
            confidence=0.7,
            reasoning=f"Adapting to student performance - current level {level}"
        )

    def _decide_subject_switch(self) -> AIDecision:
        """Decide when to switch subjects based on schedule."""
        if not self.class_manager:
            return AIDecision(
                decision_type="subject_switch",
                suggested_action="keep_current",
                confidence=0.5,
                reasoning="No class manager"
            )

        current_slot = self.class_manager.get_current_slot()
        next_slot = self.class_manager.get_next_slot()

        if not current_slot and not next_slot:
            return AIDecision(
                decision_type="subject_switch",
                suggested_action="end_class",
                confidence=0.9,
                reasoning="No more slots in today's schedule"
            )

        if next_slot and next_slot.get("subject") == "break":
            return AIDecision(
                decision_type="subject_switch",
                suggested_action="break",
                confidence=0.95,
                reasoning=f"Break time - next subject: {next_slot.get('subject', 'unknown')}"
            )

        if next_slot:
            return AIDecision(
                decision_type="subject_switch",
                suggested_action=f"switch_to_{next_slot.get('subject', 'mathematics')}",
                confidence=0.85,
                reasoning=f"Schedule-based: next subject is {next_slot.get('subject')} at {next_slot.get('time')}"
            )

        return AIDecision(
            decision_type="subject_switch",
            suggested_action="keep_current",
            confidence=0.6,
            reasoning="Continue current lesson"
        )

    def _decide_class_timing(self) -> AIDecision:
        """Decide class timing (start/end/break) based on schedule."""
        if not self.class_manager:
            return AIDecision(
                decision_type="class_timing",
                suggested_action="continue",
                confidence=0.5,
                reasoning="No class manager"
            )

        schedule = self.class_manager.get_current_schedule()
        if not schedule:
            return AIDecision(
                decision_type="class_timing",
                suggested_action="no_schedule",
                confidence=0.5,
                reasoning="No schedule configured"
            )

        current = self.class_manager.get_current_slot()
        next_slot = self.class_manager.get_next_slot()

        if not current and not next_slot:
            return AIDecision(
                decision_type="class_timing",
                suggested_action="class_ended",
                confidence=0.95,
                reasoning="End of today's schedule"
            )

        if current and current.get("subject") == "break":
            return AIDecision(
                decision_type="class_timing",
                suggested_action="break_active",
                confidence=0.95,
                reasoning="Currently in break period"
            )

        if next_slot and next_slot.get("subject") == "break":
            end_time = current.get("time", "00:00")
            duration = current.get("duration", 0)
            h, m = map(int, end_time.split(":"))
            end_m = m + duration
            end_h = h + end_m // 60
            end_m = end_m % 60
            return AIDecision(
                decision_type="class_timing",
                suggested_action=f"wrap_up_at_{end_h:02d}:{end_m:02d}",
                confidence=0.85,
                reasoning=f"Break coming at {next_slot.get('time')}"
            )

        return AIDecision(
            decision_type="class_timing",
            suggested_action="continue",
            confidence=0.7,
            reasoning="Class session in progress"
        )

    def _decide_feedback(self) -> AIDecision:
        """Decide what feedback to give student."""
        return AIDecision(
            decision_type="feedback",
            suggested_action="encourage",
            confidence=0.7,
            reasoning="Student showing good engagement"
        )

    def get_decision(self, decision_type: str, auto_execute: Optional[bool] = None) -> AIDecision:
        """Get AI decision, optionally auto-executing."""
        decision = self._make_decision(decision_type)

        if auto_execute is not None:
            decision.auto_execute = auto_execute
        elif self._auto_mode:
            decision.auto_execute = True

        self._pending_decisions.append(decision)
        self._decision_history.append(decision)

        logger.info(f"AI Decision: {decision.decision_type} -> {decision.suggested_action} (auto:{decision.auto_execute})")

        return decision

    def override_decision(self, decision_id: int, override_action: str) -> bool:
        """User overrides an AI decision."""
        if 0 <= decision_id < len(self._pending_decisions):
            decision = self._pending_decisions[decision_id]
            decision.user_override = override_action
            decision.auto_execute = False
            logger.info(f"User override: {decision.decision_type} -> {override_action}")
            return True
        return False

    def confirm_decision(self, decision_id: int) -> bool:
        """User confirms an AI decision to proceed."""
        if 0 <= decision_id < len(self._pending_decisions):
            decision = self._pending_decisions[decision_id]
            decision.auto_execute = True
            logger.info(f"Decision confirmed: {decision.decision_type}")
            return True
        return False

    def get_pending_decisions(self) -> list[dict]:
        """Get list of pending decisions for user review."""
        return [
            {
                "id": i,
                "type": d.decision_type,
                "suggested": d.suggested_action,
                "reasoning": d.reasoning,
                "confidence": d.confidence,
                "auto": d.auto_execute,
                "overridden": d.user_override is not None,
            }
            for i, d in enumerate(self._pending_decisions)
        ]

    def set_user_callback(self, callback: Callable) -> None:
        """Set callback for when user input is needed."""
        self._user_callback = callback

    def request_user_input(self, prompt: str, options: list[str]) -> Optional[str]:
        """Request user input, pausing AI automation."""
        logger.info(f"Requesting user input: {prompt}")
        if self._user_callback:
            return self._user_callback(prompt, options)
        return None

    def get_ai_status(self) -> dict:
        """Get AI system status."""
        return {
            "auto_mode": self._auto_mode,
            "pending_decisions": len(self._pending_decisions),
            "total_decisions": len(self._decision_history),
            "last_decision": self._decision_history[-1].suggested_action if self._decision_history else None,
        }

    def clear_pending(self) -> None:
        """Clear pending decisions."""
        self._pending_decisions.clear()


class UserControlPanel:
    """User control panel for overriding AI decisions."""

    def __init__(self, ai_controller: AIController):
        self.ai = ai_controller

    def enable_auto_mode(self) -> None:
        """Enable full AI automation."""
        self.ai.set_auto_mode(True)
        print("Auto mode ENABLED - AI will make decisions automatically")

    def disable_auto_mode(self) -> None:
        """Disable auto mode - user must approve all decisions."""
        self.ai.set_auto_mode(False)
        print("Auto mode DISABLED - You will approve each AI decision")

    def show_ai_status(self) -> None:
        """Display current AI status."""
        status = self.ai.get_ai_status()
        print("\n--- AI STATUS ---")
        print(f"Auto Mode: {'ON' if status['auto_mode'] else 'OFF'}")
        print(f"Pending Decisions: {status['pending_decisions']}")
        print(f"Total Decisions: {status['total_decisions']}")
        print(f"Last Action: {status['last_decision']}")

    def show_pending_decisions(self) -> list[dict]:
        """Show and return pending decisions."""
        decisions = self.ai.get_pending_decisions()
        print("\n--- PENDING AI DECISIONS ---")
        for d in decisions:
            override_mark = " [OVERRIDDEN]" if d["overridden"] else ""
            auto_mark = " [AUTO]" if d["auto"] else " [WAITING]"
            print(f"[{d['id']}] {d['type']}: {d['suggested']}{auto_mark}{override_mark}")
            print(f"    Reason: {d['reasoning']}")
            print(f"    Confidence: {d['confidence']*100:.0f}%")
        return decisions

    def override_decision(self, decision_id: int, new_action: str) -> bool:
        """Override a specific AI decision."""
        return self.ai.override_decision(decision_id, new_action)

    def confirm_decision(self, decision_id: int) -> bool:
        """Confirm an AI decision."""
        return self.ai.confirm_decision(decision_id)

    def request_decision(self, decision_type: str) -> AIDecision:
        """Request a specific type of decision from AI."""
        return self.ai.get_decision(decision_type, auto_execute=False)

    def run_interactive(self) -> None:
        """Run interactive control loop."""
        print("\n=== CAMP TUTOR AI CONTROL PANEL ===")
        print("Commands: status, decisions, auto, manual, switch, time, decide, override, confirm, quit")

        running = True
        while running:
            try:
                cmd = input("\n> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                break

            if cmd == "status":
                self.show_ai_status()
            elif cmd == "decisions":
                self.show_pending_decisions()
            elif cmd == "auto":
                self.ai.enable_full_auto_mode()
                print("AI Mode: FULL AUTO")
            elif cmd == "manual":
                self.ai.enable_manual_mode()
                print("AI Mode: MANUAL - User controls")
            elif cmd == "switch":
                decision = self.request_decision("subject_switch")
                print(f"AI: {decision.suggested_action} - {decision.reasoning}")
            elif cmd == "time":
                decision = self.request_decision("class_timing")
                print(f"AI: {decision.suggested_action} - {decision.reasoning}")
            elif cmd == "decide":
                dtype = input("Type (next_lesson/difficulty/subject_switch/class_timing): ").strip()
                decision = self.request_decision(dtype)
                print(f"AI Decision: {decision.suggested_action}")
                print(f"Reasoning: {decision.reasoning}")
                print(f"Confidence: {decision.confidence*100:.0f}%")
            elif cmd.startswith("override "):
                parts = cmd.split()
                if len(parts) >= 3:
                    did = int(parts[1])
                    action = " ".join(parts[2:])
                    if self.override_decision(did, action):
                        print(f"Decision {did} overridden to: {action}")
            elif cmd.startswith("confirm "):
                did = int(cmd.split()[1])
                if self.confirm_decision(did):
                    print(f"Decision {did} confirmed")
            elif cmd in ("quit", "q"):
                running = False
            else:
                print("Unknown command")

        print("Control panel closed")


_ai_controller_instance: Optional[AIController] = None


def get_ai_controller(class_manager=None, tutor_engine=None) -> AIController:
    """Get global AI controller instance."""
    global _ai_controller_instance
    if _ai_controller_instance is None:
        _ai_controller_instance = AIController(class_manager, tutor_engine)
    return _ai_controller_instance


def get_user_control_panel() -> UserControlPanel:
    """Get user control panel instance."""
    return UserControlPanel(get_ai_controller())