"""
Conversation Analyst Agent for MemoryChat Multi-Agent application.
Analyzes conversation patterns and provides insights.
"""
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import Counter, defaultdict

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from config.agent_config import CONVERSATION_ANALYST_AGENT
from config.logging_config import get_agent_logger
from services.database_service import DatabaseService
from database.database import SessionLocal


class ConversationAnalystAgent(BaseAgent):
    """
    Agent that analyzes conversations and provides insights.
    
    Responsibilities:
    - Analyze conversation patterns
    - Detect sentiment and emotions
    - Identify topics and themes
    - Track engagement metrics
    - Generate insights and recommendations
    """
    
    def __init__(self):
        """Initialize Conversation Analyst Agent with configuration."""
        config = CONVERSATION_ANALYST_AGENT
        super().__init__(
            name=config["name"],
            description=config["description"],
            llm_model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            system_prompt=config["system_prompt"]
        )
        
        # Analysis thresholds
        self.min_messages_for_analysis = 2
        self.periodic_analysis_interval = 5  # Analyze every 5 messages
        
        # Sentiment keywords (simple approach)
        self.positive_keywords = [
            "great", "good", "excellent", "wonderful", "amazing", "love", "like",
            "happy", "pleased", "satisfied", "thanks", "thank", "appreciate"
        ]
        self.negative_keywords = [
            "bad", "terrible", "awful", "hate", "dislike", "unhappy", "angry",
            "frustrated", "disappointed", "problem", "issue", "error", "wrong"
        ]
        
        # Engagement indicators
        self.engagement_indicators = [
            "question", "ask", "tell me", "explain", "how", "what", "why",
            "describe", "detail", "more", "elaborate"
        ]
        
        # Prompt templates
        self.sentiment_analysis_prompt = """Analyze the sentiment of these messages:

{messages}

Determine the overall sentiment: positive, negative, neutral, or mixed.
Return JSON: {{"sentiment": "positive|negative|neutral|mixed", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""

        self.topic_extraction_prompt = """Extract the main topics and themes from these messages:

{messages}

Return JSON array of topics: [{{"topic": "topic name", "relevance": 0.0-1.0}}]"""

        self.pattern_detection_prompt = """Analyze this conversation history for patterns:

{history}

Identify recurring topics, behaviors, or themes.
Return JSON: {{"patterns": ["pattern1", "pattern2"], "frequency": {{"pattern1": 3}}}}"""

    def execute(self, input_data: AgentInput, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Execute conversation analysis.
        
        Args:
            input_data: Standard input format with:
                - session_id: int
                - user_message: str
                - privacy_mode: str
                - profile_id: int
                - context: dict (may contain 'conversation_history', 'existing_memories', etc.)
            context: Optional additional context
            
        Returns:
            Standard output format with analysis results
        """
        try:
            # Get input data
            session_id = input_data.get("session_id")
            conversation_history = input_data.get("context", {}).get("conversation_history", [])
            existing_memories = input_data.get("context", {}).get("existing_memories", [])
            profile_id = input_data.get("profile_id")
            
            if not conversation_history or len(conversation_history) < self.min_messages_for_analysis:
                self.logger.info("Not enough messages for analysis")
                return {
                    "success": True,
                    "data": {
                        "analysis": {},
                        "insights": {},
                        "recommendations": [],
                        "skipped": True,
                        "reason": "insufficient_messages",
                    },
                    "tokens_used": 0,
                    "execution_time_ms": 0,
                }
            
            # Perform analysis
            sentiment_result = self._analyze_sentiment(conversation_history)
            topics_result = self._extract_topics(conversation_history)
            patterns_result = self._detect_patterns(conversation_history)
            engagement_result = self._calculate_engagement(conversation_history)
            memory_gaps = self._identify_memory_gaps(conversation_history, existing_memories)
            
            # Generate insights
            insights = self._generate_insights(
                sentiment=sentiment_result,
                topics=topics_result,
                patterns=patterns_result,
                engagement=engagement_result,
                memory_gaps=memory_gaps,
                conversation_history=conversation_history
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                sentiment=sentiment_result,
                topics=topics_result,
                patterns=patterns_result,
                engagement=engagement_result,
                memory_gaps=memory_gaps,
                profile_id=profile_id
            )
            
            # Store insights if session_id provided
            if session_id:
                self._store_insights(session_id, insights, recommendations)
            
            self.logger.info(f"Analysis completed for session {session_id}: {len(topics_result)} topics, sentiment={sentiment_result.get('sentiment', 'unknown')}")
            
            return {
                "success": True,
                "data": {
                    "analysis": {
                        "sentiment": sentiment_result,
                        "topics": topics_result,
                        "patterns": patterns_result,
                        "engagement": engagement_result,
                        "memory_gaps": memory_gaps,
                    },
                    "insights": insights,
                    "recommendations": recommendations,
                },
                "tokens_used": self._count_tokens(str(insights) + str(recommendations)),
                "execution_time_ms": 0,  # Will be set by wrapper
            }
            
        except Exception as e:
            self.logger.error(f"Error in conversation analysis: {str(e)}", exc_info=True)
            return {
                "success": False,
                "data": {"analysis": {}, "insights": {}, "recommendations": []},
                "error": f"Conversation analysis failed: {str(e)}",
                "tokens_used": 0,
                "execution_time_ms": 0,
            }
    
    def _analyze_sentiment(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze sentiment of messages.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            # Simple keyword-based sentiment analysis
            all_text = " ".join([msg.get("content", "") for msg in messages])
            text_lower = all_text.lower()
            
            positive_count = sum(1 for keyword in self.positive_keywords if keyword in text_lower)
            negative_count = sum(1 for keyword in self.negative_keywords if keyword in text_lower)
            
            # Determine sentiment
            if positive_count > negative_count and positive_count > 0:
                sentiment = "positive"
                confidence = min(1.0, positive_count / max(1, len(messages)))
            elif negative_count > positive_count and negative_count > 0:
                sentiment = "negative"
                confidence = min(1.0, negative_count / max(1, len(messages)))
            elif positive_count > 0 and negative_count > 0:
                sentiment = "mixed"
                confidence = 0.5
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            return {
                "sentiment": sentiment,
                "confidence": round(confidence, 2),
                "positive_indicators": positive_count,
                "negative_indicators": negative_count,
                "reasoning": f"Found {positive_count} positive and {negative_count} negative indicators",
            }
            
        except Exception as e:
            self.logger.warning(f"Sentiment analysis failed: {str(e)}")
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "error": str(e),
            }
    
    def _extract_topics(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract main topics and themes from messages.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            List of topic dictionaries
        """
        try:
            # Simple keyword extraction approach
            all_text = " ".join([msg.get("content", "") for msg in messages])
            
            # Extract significant words (4+ characters, not stop words)
            stop_words = {
                "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
                "been", "have", "has", "had", "do", "does", "did", "will", "would",
                "could", "should", "this", "that", "these", "those", "i", "you",
                "he", "she", "it", "we", "they", "what", "which", "who", "when",
                "where", "why", "how"
            }
            
            words = re.findall(r'\b[a-z]{4,}\b', all_text.lower())
            significant_words = [w for w in words if w not in stop_words]
            
            # Count word frequency
            word_counts = Counter(significant_words)
            
            # Get top topics
            top_words = word_counts.most_common(10)
            
            topics = []
            for word, count in top_words:
                relevance = min(1.0, count / max(1, len(messages)))
                if relevance >= 0.1:  # At least 10% relevance
                    topics.append({
                        "topic": word,
                        "relevance": round(relevance, 2),
                        "frequency": count,
                    })
            
            return topics[:5]  # Return top 5 topics
            
        except Exception as e:
            self.logger.warning(f"Topic extraction failed: {str(e)}")
            return []
    
    def _detect_patterns(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect recurring patterns in conversation history.
        
        Args:
            conversation_history: List of message dictionaries
            
        Returns:
            Dictionary with detected patterns
        """
        try:
            # Group messages by role
            user_messages = [msg.get("content", "") for msg in conversation_history if msg.get("role") == "user"]
            assistant_messages = [msg.get("content", "") for msg in conversation_history if msg.get("role") == "assistant"]
            
            patterns = []
            frequencies = {}
            
            # Detect question patterns
            question_count = sum(1 for msg in user_messages if "?" in msg)
            if question_count >= 2:
                patterns.append("frequent_questions")
                frequencies["frequent_questions"] = question_count
            
            # Detect topic repetition
            all_user_text = " ".join(user_messages).lower()
            words = re.findall(r'\b[a-z]{4,}\b', all_user_text)
            word_counts = Counter(words)
            repeated_topics = [word for word, count in word_counts.items() if count >= 3]
            if repeated_topics:
                patterns.append("recurring_topics")
                frequencies["recurring_topics"] = len(repeated_topics)
            
            # Detect engagement patterns
            engagement_count = sum(
                1 for msg in user_messages
                if any(indicator in msg.lower() for indicator in self.engagement_indicators)
            )
            if engagement_count >= 2:
                patterns.append("high_engagement")
                frequencies["high_engagement"] = engagement_count
            
            return {
                "patterns": patterns,
                "frequencies": frequencies,
                "pattern_count": len(patterns),
            }
            
        except Exception as e:
            self.logger.warning(f"Pattern detection failed: {str(e)}")
            return {
                "patterns": [],
                "frequencies": {},
                "pattern_count": 0,
            }
    
    def _calculate_engagement(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate user engagement metrics.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Dictionary with engagement metrics
        """
        try:
            user_messages = [msg for msg in messages if msg.get("role") == "user"]
            
            if not user_messages:
                return {
                    "score": 0.0,
                    "level": "low",
                    "metrics": {},
                }
            
            # Calculate metrics
            total_messages = len(user_messages)
            avg_length = sum(len(msg.get("content", "")) for msg in user_messages) / max(1, total_messages)
            
            # Count engagement indicators
            engagement_indicators_count = sum(
                1 for msg in user_messages
                if any(indicator in msg.get("content", "").lower() for indicator in self.engagement_indicators)
            )
            
            # Count questions
            question_count = sum(1 for msg in user_messages if "?" in msg.get("content", ""))
            
            # Calculate engagement score (0.0 to 1.0)
            length_score = min(1.0, avg_length / 100.0)  # Normalize to 100 chars
            indicator_score = min(1.0, engagement_indicators_count / max(1, total_messages))
            question_score = min(1.0, question_count / max(1, total_messages))
            
            engagement_score = (length_score * 0.3 + indicator_score * 0.4 + question_score * 0.3)
            
            # Determine level
            if engagement_score >= 0.7:
                level = "high"
            elif engagement_score >= 0.4:
                level = "medium"
            else:
                level = "low"
            
            return {
                "score": round(engagement_score, 2),
                "level": level,
                "metrics": {
                    "total_messages": total_messages,
                    "avg_message_length": round(avg_length, 1),
                    "engagement_indicators": engagement_indicators_count,
                    "questions": question_count,
                },
            }
            
        except Exception as e:
            self.logger.warning(f"Engagement calculation failed: {str(e)}")
            return {
                "score": 0.5,
                "level": "medium",
                "metrics": {},
            }
    
    def _identify_memory_gaps(
        self,
        conversation: List[Dict[str, Any]],
        existing_memories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify missing information that could be useful.
        
        Args:
            conversation: List of conversation messages
            existing_memories: List of existing memory dictionaries
            
        Returns:
            List of identified memory gaps
        """
        try:
            gaps = []
            
            # Extract topics from conversation
            conversation_text = " ".join([msg.get("content", "") for msg in conversation])
            conversation_topics = set(re.findall(r'\b[a-z]{4,}\b', conversation_text.lower()))
            
            # Extract topics from existing memories
            memory_text = " ".join([
                mem.get("content", "") if isinstance(mem, dict) else str(mem)
                for mem in existing_memories
            ])
            memory_topics = set(re.findall(r'\b[a-z]{4,}\b', memory_text.lower()))
            
            # Find gaps (topics in conversation but not in memories)
            gap_topics = conversation_topics - memory_topics
            
            # Filter significant gaps (common words)
            stop_words = {"this", "that", "with", "from", "have", "been", "will", "would"}
            significant_gaps = [topic for topic in gap_topics if topic not in stop_words and len(topic) >= 4]
            
            for topic in significant_gaps[:5]:  # Limit to 5 gaps
                gaps.append({
                    "topic": topic,
                    "suggestion": f"Consider storing information about {topic}",
                    "priority": "medium",
                })
            
            return gaps
            
        except Exception as e:
            self.logger.warning(f"Memory gap identification failed: {str(e)}")
            return []
    
    def _generate_insights(
        self,
        sentiment: Dict[str, Any],
        topics: List[Dict[str, Any]],
        patterns: Dict[str, Any],
        engagement: Dict[str, Any],
        memory_gaps: List[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights from analysis.
        
        Args:
            sentiment: Sentiment analysis results
            topics: Topic extraction results
            patterns: Pattern detection results
            engagement: Engagement calculation results
            memory_gaps: Memory gap identification results
            conversation_history: Conversation history
            
        Returns:
            Dictionary with insights
        """
        # Session summary
        session_summary = f"Conversation with {len(conversation_history)} messages. "
        session_summary += f"Overall sentiment: {sentiment.get('sentiment', 'unknown')}. "
        session_summary += f"Engagement level: {engagement.get('level', 'unknown')}."
        
        # Topic distribution
        topic_distribution = {
            topic["topic"]: topic["relevance"]
            for topic in topics
        }
        
        # Sentiment trends
        sentiment_trends = {
            "overall": sentiment.get("sentiment", "neutral"),
            "confidence": sentiment.get("confidence", 0.5),
            "indicators": {
                "positive": sentiment.get("positive_indicators", 0),
                "negative": sentiment.get("negative_indicators", 0),
            },
        }
        
        # Memory effectiveness (simplified)
        memory_effectiveness = {
            "gaps_identified": len(memory_gaps),
            "coverage": 1.0 - (len(memory_gaps) / max(1, len(topics))),
        }
        
        # Profile fit score (simplified)
        profile_fit_score = 0.7  # Default, would be calculated based on profile vs conversation
        
        return {
            "session_summary": session_summary,
            "topic_distribution": topic_distribution,
            "sentiment_trends": sentiment_trends,
            "engagement_metrics": engagement.get("metrics", {}),
            "memory_effectiveness": memory_effectiveness,
            "profile_fit_score": profile_fit_score,
            "pattern_summary": patterns.get("patterns", []),
        }
    
    def _generate_recommendations(
        self,
        sentiment: Dict[str, Any],
        topics: List[Dict[str, Any]],
        patterns: Dict[str, Any],
        engagement: Dict[str, Any],
        memory_gaps: List[Dict[str, Any]],
        profile_id: Optional[int]
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on analysis.
        
        Args:
            sentiment: Sentiment analysis results
            topics: Topic extraction results
            patterns: Pattern detection results
            engagement: Engagement calculation results
            memory_gaps: Memory gap identification results
            profile_id: Current profile ID
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Memory gap recommendations
        if memory_gaps:
            recommendations.append({
                "type": "memory_organization",
                "priority": "medium",
                "message": f"Consider storing information about {len(memory_gaps)} topics: {', '.join([g['topic'] for g in memory_gaps[:3]])}",
                "action": "review_memory_gaps",
            })
        
        # Engagement recommendations
        if engagement.get("level") == "low":
            recommendations.append({
                "type": "engagement",
                "priority": "high",
                "message": "User engagement is low. Consider asking more engaging questions.",
                "action": "increase_engagement",
            })
        
        # Sentiment recommendations
        if sentiment.get("sentiment") == "negative":
            recommendations.append({
                "type": "sentiment",
                "priority": "high",
                "message": "Negative sentiment detected. Consider adjusting approach.",
                "action": "address_concerns",
            })
        
        # Pattern-based recommendations
        if "recurring_topics" in patterns.get("patterns", []):
            recommendations.append({
                "type": "pattern",
                "priority": "medium",
                "message": "Recurring topics detected. User may have strong interest in these areas.",
                "action": "explore_topics",
            })
        
        # Follow-up question suggestions
        if topics:
            top_topic = topics[0]["topic"] if topics else None
            if top_topic:
                recommendations.append({
                    "type": "follow_up",
                    "priority": "low",
                    "message": f"Consider asking follow-up questions about {top_topic}",
                    "action": "suggest_questions",
                })
        
        return recommendations
    
    def _recommend_memory_profile_switch(
        self,
        analysis: Dict[str, Any],
        available_profiles: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Recommend switching memory profile based on analysis.
        
        Args:
            analysis: Analysis results
            available_profiles: List of available profiles
            
        Returns:
            Recommendation dictionary or None
        """
        # Simplified: would analyze profile fit and suggest switch if needed
        # For now, return None (no recommendation)
        return None
    
    def _suggest_follow_up_questions(self, current_topic: str) -> List[str]:
        """
        Suggest follow-up questions based on current topic.
        
        Args:
            current_topic: Current discussion topic
            
        Returns:
            List of suggested questions
        """
        suggestions = [
            f"Tell me more about {current_topic}",
            f"What do you think about {current_topic}?",
            f"How does {current_topic} relate to your interests?",
        ]
        return suggestions[:3]
    
    def _suggest_memory_organization(self, current_memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Suggest memory organization improvements.
        
        Args:
            current_memories: List of current memories
            
        Returns:
            Dictionary with organization suggestions
        """
        # Analyze memory distribution
        memory_types = Counter([mem.get("memory_type", "other") for mem in current_memories if isinstance(mem, dict)])
        
        suggestions = {
            "distribution": dict(memory_types),
            "recommendations": [],
        }
        
        # Suggest balance if one type dominates
        if len(memory_types) > 0:
            most_common_type = memory_types.most_common(1)[0][0]
            if memory_types[most_common_type] / len(current_memories) > 0.7:
                suggestions["recommendations"].append(
                    f"Consider diversifying memory types. {most_common_type} dominates."
                )
        
        return suggestions
    
    def _store_insights(
        self,
        session_id: int,
        insights: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> None:
        """
        Store insights in database for later retrieval.
        
        Args:
            session_id: Session ID
            insights: Insights dictionary
            recommendations: Recommendations list
        """
        try:
            db = SessionLocal()
            db_service = DatabaseService(db)
            
            # Store as agent log
            db_service.log_agent_action(
                session_id=session_id,
                agent_name=self.name,
                action="conversation_analysis",
                input_data={"session_id": session_id},
                output_data={
                    "insights": insights,
                    "recommendations": recommendations,
                },
                status="success"
            )
            
            db.close()
            
            self.logger.debug(f"Stored insights for session {session_id}")
            
        except Exception as e:
            self.logger.warning(f"Failed to store insights: {str(e)}")


