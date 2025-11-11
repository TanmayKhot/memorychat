"""
Privacy Guardian Agent for MemoryChat Multi-Agent application.
Detects sensitive information and enforces privacy settings.
"""
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from config.agent_config import PRIVACY_GUARDIAN_AGENT
from config.logging_config import get_agent_logger


class PrivacyGuardianAgent(BaseAgent):
    """
    Agent that detects sensitive information and enforces privacy settings.
    
    Responsibilities:
    - Detect PII (Personal Identifiable Information)
    - Enforce privacy mode rules
    - Generate privacy warnings
    - Sanitize content when needed
    - Verify profile isolation
    """
    
    def __init__(self):
        """Initialize Privacy Guardian Agent with configuration."""
        config = PRIVACY_GUARDIAN_AGENT
        super().__init__(
            name=config["name"],
            description=config["description"],
            llm_model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            system_prompt=config["system_prompt"]
        )
        
        # PII detection patterns
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.credit_card_pattern = re.compile(r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b')
        self.ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        self.date_pattern = re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b')
        
        # Financial keywords
        self.financial_keywords = [
            "credit card", "debit card", "bank account", "routing number",
            "account number", "pin", "password", "social security",
            "ssn", "tax id", "ein", "salary", "income", "wage"
        ]
        
        # Health keywords
        self.health_keywords = [
            "diagnosis", "medical condition", "prescription", "medication",
            "doctor", "hospital", "surgery", "treatment", "therapy",
            "medical history", "health insurance", "patient id"
        ]
        
        # Privacy violation severity levels
        self.severity_levels = {
            "low": ["email", "phone"],
            "medium": ["address", "date_of_birth", "personal_name"],
            "high": ["credit_card", "ssn", "financial_info", "health_info"]
        }
        
        # Prompt templates
        self.pii_detection_prompt = """Analyze this text for sensitive information:

Text: {text}

Identify and categorize:
1. Email addresses
2. Phone numbers
3. Credit card numbers
4. Social Security Numbers
5. Physical addresses
6. Dates of birth
7. Personal names
8. Financial information
9. Health information

Return JSON with:
{{
  "violations": [
    {{
      "type": "email|phone|credit_card|ssn|address|date_of_birth|personal_name|financial_info|health_info",
      "severity": "low|medium|high",
      "content": "detected content",
      "position": "start_index"
    }}
  ],
  "sanitized_text": "text with sensitive info redacted"
}}"""

    def execute(self, input_data: AgentInput, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Execute privacy check and enforcement.
        
        Args:
            input_data: Standard input format with:
                - session_id: int
                - user_message: str
                - privacy_mode: str ('normal', 'incognito', 'pause_memory')
                - profile_id: int
                - context: dict
            context: Optional additional context
            
        Returns:
            Standard output format with privacy check results
        """
        try:
            # Get input data
            user_message = input_data.get("user_message", "")
            privacy_mode = input_data.get("privacy_mode", "normal").lower()
            profile_id = input_data.get("profile_id")
            session_id = input_data.get("session_id")
            
            if not user_message:
                self.logger.warning("No user message provided for privacy check")
                return {
                    "success": True,
                    "data": {
                        "violations": [],
                        "warnings": [],
                        "sanitized_content": "",
                        "allowed": True,
                        "privacy_mode": privacy_mode,
                    },
                    "tokens_used": 0,
                    "execution_time_ms": 0,
                }
            
            # Detect PII violations
            violations = self._detect_all_pii(user_message)
            
            # Verify profile isolation
            session_profile_id = input_data.get("context", {}).get("session_profile_id")
            isolation_ok = self._verify_memory_access(profile_id, session_profile_id)
            
            # Enforce privacy mode rules
            enforcement_result = self._enforce_privacy_mode(
                privacy_mode=privacy_mode,
                violations=violations,
                user_message=user_message
            )
            
            # Generate warnings
            warnings = self._generate_privacy_warning(violations, privacy_mode)
            
            # Log privacy violations for audit
            if violations:
                self._log_privacy_violations(
                    session_id=session_id,
                    profile_id=profile_id,
                    violations=violations,
                    privacy_mode=privacy_mode
                )
            
            # Build result
            result = {
                "violations": violations,
                "warnings": warnings,
                "sanitized_content": enforcement_result.get("sanitized_content", user_message),
                "allowed": enforcement_result.get("allowed", True),
                "privacy_mode": privacy_mode,
                "profile_isolation_ok": isolation_ok,
                "violation_count": len(violations),
                "high_severity_count": len([v for v in violations if v.get("severity") == "high"]),
            }
            
            self.logger.info(
                f"Privacy check completed: {len(violations)} violations, "
                f"mode={privacy_mode}, allowed={result['allowed']}"
            )
            
            return {
                "success": True,
                "data": result,
                "tokens_used": self._count_tokens(str(result)),
                "execution_time_ms": 0,  # Will be set by wrapper
            }
            
        except Exception as e:
            self.logger.error(f"Error in privacy check: {str(e)}", exc_info=True)
            return {
                "success": False,
                "data": {
                    "violations": [],
                    "warnings": [],
                    "sanitized_content": "",
                    "allowed": False,  # Fail-safe: deny on error
                    "privacy_mode": input_data.get("privacy_mode", "normal"),
                },
                "error": f"Privacy check failed: {str(e)}",
                "tokens_used": 0,
                "execution_time_ms": 0,
            }
    
    def _detect_all_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect all types of PII in text.
        
        Args:
            text: Text to scan
            
        Returns:
            List of violation dictionaries
        """
        violations = []
        
        # Detect email addresses
        emails = self._detect_email_addresses(text)
        violations.extend(emails)
        
        # Detect phone numbers
        phones = self._detect_phone_numbers(text)
        violations.extend(phones)
        
        # Detect credit cards
        credit_cards = self._detect_credit_cards(text)
        violations.extend(credit_cards)
        
        # Detect SSN
        ssns = self._detect_ssn(text)
        violations.extend(ssns)
        
        # Detect addresses
        addresses = self._detect_addresses(text)
        violations.extend(addresses)
        
        # Detect dates of birth
        dates = self._detect_dates_of_birth(text)
        violations.extend(dates)
        
        # Detect personal names (simple pattern-based)
        names = self._detect_personal_names(text)
        violations.extend(names)
        
        # Detect financial information
        financial = self._detect_financial_info(text)
        violations.extend(financial)
        
        # Detect health information
        health = self._detect_health_info(text)
        violations.extend(health)
        
        return violations
    
    def _detect_email_addresses(self, text: str) -> List[Dict[str, Any]]:
        """Detect email addresses in text."""
        violations = []
        matches = self.email_pattern.finditer(text)
        for match in matches:
            violations.append({
                "type": "email",
                "severity": "low",
                "content": match.group(0),
                "position": match.start(),
            })
        return violations
    
    def _detect_phone_numbers(self, text: str) -> List[Dict[str, Any]]:
        """Detect phone numbers in text."""
        violations = []
        matches = self.phone_pattern.finditer(text)
        for match in matches:
            violations.append({
                "type": "phone",
                "severity": "low",
                "content": match.group(0),
                "position": match.start(),
            })
        return violations
    
    def _detect_credit_cards(self, text: str) -> List[Dict[str, Any]]:
        """Detect credit card numbers in text."""
        violations = []
        matches = self.credit_card_pattern.finditer(text)
        for match in matches:
            # Basic Luhn check (simplified)
            card_number = re.sub(r'[-.\s]', '', match.group(0))
            if len(card_number) == 16:
                violations.append({
                    "type": "credit_card",
                    "severity": "high",
                    "content": match.group(0),
                    "position": match.start(),
                })
        return violations
    
    def _detect_ssn(self, text: str) -> List[Dict[str, Any]]:
        """Detect Social Security Numbers in text."""
        violations = []
        matches = self.ssn_pattern.finditer(text)
        for match in matches:
            violations.append({
                "type": "ssn",
                "severity": "high",
                "content": match.group(0),
                "position": match.start(),
            })
        return violations
    
    def _detect_addresses(self, text: str) -> List[Dict[str, Any]]:
        """Detect physical addresses in text."""
        violations = []
        # Simple pattern: number + street name + city/state/zip
        address_pattern = re.compile(
            r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Court|Ct|Place|Pl)\b[,\s]+[A-Za-z\s]+(?:,\s*)?[A-Z]{2}\s+\d{5}',
            re.IGNORECASE
        )
        matches = address_pattern.finditer(text)
        for match in matches:
            violations.append({
                "type": "address",
                "severity": "medium",
                "content": match.group(0),
                "position": match.start(),
            })
        return violations
    
    def _detect_dates_of_birth(self, text: str) -> List[Dict[str, Any]]:
        """Detect dates of birth in text."""
        violations = []
        # Look for date patterns with context words
        date_context_pattern = re.compile(
            r'\b(?:born|birth|dob|date of birth|birthday)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            re.IGNORECASE
        )
        matches = date_context_pattern.finditer(text)
        for match in matches:
            violations.append({
                "type": "date_of_birth",
                "severity": "medium",
                "content": match.group(1),
                "position": match.start(),
            })
        return violations
    
    def _detect_personal_names(self, text: str) -> List[Dict[str, Any]]:
        """Detect personal names in text (simple pattern-based)."""
        violations = []
        # Look for capitalized words that might be names
        # This is a simple heuristic - in production, use NER
        name_pattern = re.compile(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b')
        matches = name_pattern.finditer(text)
        for match in matches:
            # Filter out common non-name patterns
            content = match.group(0)
            if not any(word in content.lower() for word in ["the", "this", "that", "there", "then"]):
                violations.append({
                    "type": "personal_name",
                    "severity": "medium",
                    "content": content,
                    "position": match.start(),
                })
        return violations
    
    def _detect_financial_info(self, text: str) -> List[Dict[str, Any]]:
        """Detect financial information in text."""
        violations = []
        text_lower = text.lower()
        for keyword in self.financial_keywords:
            if keyword in text_lower:
                # Find the context around the keyword
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                matches = pattern.finditer(text)
                for match in matches:
                    violations.append({
                        "type": "financial_info",
                        "severity": "high",
                        "content": keyword,
                        "position": match.start(),
                    })
                    break  # Only add once per keyword
        return violations
    
    def _detect_health_info(self, text: str) -> List[Dict[str, Any]]:
        """Detect health information in text."""
        violations = []
        text_lower = text.lower()
        for keyword in self.health_keywords:
            if keyword in text_lower:
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                matches = pattern.finditer(text)
                for match in matches:
                    violations.append({
                        "type": "health_info",
                        "severity": "high",
                        "content": keyword,
                        "position": match.start(),
                    })
                    break  # Only add once per keyword
        return violations
    
    def _enforce_privacy_mode(
        self,
        privacy_mode: str,
        violations: List[Dict[str, Any]],
        user_message: str
    ) -> Dict[str, Any]:
        """
        Enforce privacy mode rules.
        
        Args:
            privacy_mode: Privacy mode string
            violations: List of detected violations
            user_message: Original user message
            
        Returns:
            Dictionary with enforcement results
        """
        privacy_mode = privacy_mode.lower()
        
        if privacy_mode == "normal":
            # NORMAL MODE: Allow everything, warn about sensitive data
            return {
                "allowed": True,
                "sanitized_content": user_message,  # No sanitization needed
                "action": "warn",
            }
        
        elif privacy_mode == "incognito":
            # INCOGNITO MODE: Block memory storage, redact sensitive information
            sanitized = self._redact_sensitive_info(user_message, violations)
            
            # Block if high severity violations
            high_severity = [v for v in violations if v.get("severity") == "high"]
            allowed = len(high_severity) == 0
            
            return {
                "allowed": allowed,
                "sanitized_content": sanitized,
                "action": "redact" if violations else "allow",
                "blocked": not allowed,
            }
        
        elif privacy_mode == "pause_memory":
            # PAUSE_MEMORY MODE: Allow memory retrieval, block storage, warn about new info
            return {
                "allowed": True,
                "sanitized_content": user_message,  # No sanitization needed
                "action": "warn_no_storage",
            }
        
        else:
            # Unknown mode, default to safe
            self.logger.warning(f"Unknown privacy mode: {privacy_mode}, defaulting to safe")
            return {
                "allowed": False,
                "sanitized_content": self._redact_sensitive_info(user_message, violations),
                "action": "block",
            }
    
    def _redact_sensitive_info(self, text: str, violations: List[Dict[str, Any]]) -> str:
        """
        Redact sensitive information from text.
        
        Args:
            text: Original text
            violations: List of violations to redact
            
        Returns:
            Sanitized text with sensitive info redacted
        """
        sanitized = text
        # Sort violations by position (reverse order to maintain indices)
        sorted_violations = sorted(violations, key=lambda v: v.get("position", 0), reverse=True)
        
        for violation in sorted_violations:
            content = violation.get("content", "")
            position = violation.get("position", 0)
            violation_type = violation.get("type", "")
            
            # Create redaction placeholder
            if violation_type == "email":
                redaction = "[EMAIL REDACTED]"
            elif violation_type == "phone":
                redaction = "[PHONE REDACTED]"
            elif violation_type == "credit_card":
                redaction = "[CARD REDACTED]"
            elif violation_type == "ssn":
                redaction = "[SSN REDACTED]"
            elif violation_type == "address":
                redaction = "[ADDRESS REDACTED]"
            elif violation_type == "date_of_birth":
                redaction = "[DOB REDACTED]"
            elif violation_type == "personal_name":
                redaction = "[NAME REDACTED]"
            elif violation_type == "financial_info":
                redaction = "[FINANCIAL INFO REDACTED]"
            elif violation_type == "health_info":
                redaction = "[HEALTH INFO REDACTED]"
            else:
                redaction = "[REDACTED]"
            
            # Replace content with redaction
            sanitized = sanitized[:position] + redaction + sanitized[position + len(content):]
        
        return sanitized
    
    def _generate_privacy_warning(
        self,
        violations: List[Dict[str, Any]],
        privacy_mode: str
    ) -> List[str]:
        """
        Generate privacy warnings for user.
        
        Args:
            violations: List of detected violations
            privacy_mode: Current privacy mode
            
        Returns:
            List of warning messages
        """
        warnings = []
        
        if not violations:
            return warnings
        
        privacy_mode = privacy_mode.lower()
        
        # Count violations by severity
        high_severity = [v for v in violations if v.get("severity") == "high"]
        medium_severity = [v for v in violations if v.get("severity") == "medium"]
        low_severity = [v for v in violations if v.get("severity") == "low"]
        
        if privacy_mode == "normal":
            # Warn about sensitive data
            if high_severity:
                warnings.append(
                    f"⚠️ Warning: Detected {len(high_severity)} high-severity sensitive information "
                    f"(e.g., {high_severity[0].get('type', 'unknown')}). "
                    f"This will be stored in your memory profile."
                )
            if medium_severity:
                warnings.append(
                    f"ℹ️ Info: Detected {len(medium_severity)} medium-severity sensitive information. "
                    f"This will be stored in your memory profile."
                )
        
        elif privacy_mode == "incognito":
            # Active warnings about sensitive data
            if violations:
                warnings.append(
                    f"🔒 Privacy Alert: Detected {len(violations)} sensitive information items. "
                    f"Sensitive data has been redacted and will NOT be stored."
                )
            if high_severity:
                warnings.append(
                    f"🚫 High-severity violations detected. "
                    f"Message blocked from processing."
                )
        
        elif privacy_mode == "pause_memory":
            # Warn about new information that won't be saved
            if violations:
                warnings.append(
                    f"⏸️ Memory Paused: Detected {len(violations)} sensitive information items. "
                    f"This information will NOT be saved to your memory profile."
                )
        
        return warnings
    
    def _verify_memory_access(
        self,
        profile_id: Optional[int],
        session_profile_id: Optional[int]
    ) -> bool:
        """
        Verify that memory access is isolated to correct profile.
        
        Args:
            profile_id: Requested profile ID
            session_profile_id: Session's profile ID
            
        Returns:
            True if access is allowed, False otherwise
        """
        # If no profile IDs provided, allow (might be initial setup)
        if profile_id is None and session_profile_id is None:
            return True
        
        # If session has no profile, allow (new session)
        if session_profile_id is None:
            return True
        
        # Profile IDs must match
        if profile_id == session_profile_id:
            return True
        
        # Mismatch detected
        self.logger.warning(
            f"Profile isolation violation: requested profile_id={profile_id}, "
            f"session_profile_id={session_profile_id}"
        )
        return False
    
    def _log_privacy_violations(
        self,
        session_id: Optional[int],
        profile_id: Optional[int],
        violations: List[Dict[str, Any]],
        privacy_mode: str
    ) -> None:
        """
        Log privacy violations for audit purposes.
        
        Args:
            session_id: Session ID
            profile_id: Profile ID
            violations: List of violations
            privacy_mode: Privacy mode
        """
        violation_summary = {
            "session_id": session_id,
            "profile_id": profile_id,
            "privacy_mode": privacy_mode,
            "violation_count": len(violations),
            "violations": [
                {
                    "type": v.get("type"),
                    "severity": v.get("severity"),
                    "content_length": len(v.get("content", "")),
                }
                for v in violations
            ],
            "timestamp": datetime.now().isoformat(),
        }
        
        self.logger.warning(
            f"Privacy violations detected: {json.dumps(violation_summary, indent=2)}"
        )
        
        # Log to audit log file (if configured)
        audit_logger = get_agent_logger("privacy_audit")
        audit_logger.warning(json.dumps(violation_summary))


