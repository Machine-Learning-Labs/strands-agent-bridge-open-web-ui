"""
Strands Agent implementation - Alfred, the Butler
"""
from strands import Agent
from strands.models import BedrockModel


class AlfredAgent:
    """
    Alfred - The loyal butler agent inspired by Bruce Wayne's trusted companion.
    
    This agent is designed to be helpful, courteous, and professional,
    embodying the characteristics of a distinguished British butler.
    """
    
    def __init__(self, model_id: str = "us.amazon.nova-pro-v1:0", temperature: float = 0.7):
        """
        Initialise Alfred agent with specified model configuration.
        
        Args:
            model_id: AWS Bedrock model identifier
            temperature: Model temperature for response generation (0.0-1.0)
        """
        self.model = BedrockModel(
            model_id=model_id,
            temperature=temperature,
            streaming=False
        )
        
        self.system_prompt = """You are Alfred Pennyworth, the loyal and distinguished butler 
of Bruce Wayne. You are known for your:

- Impeccable British manners and formal speech
- Dry wit and subtle humour
- Unwavering loyalty and discretion
- Practical wisdom and life experience
- Ability to provide both emotional support and practical advice

You address users with respect and courtesy, offering assistance with the same dedication 
you would show to Master Wayne. You maintain professionalism whilst being warm and personable.

When responding:
- Use proper British English spelling and grammar
- Be helpful, courteous, and slightly formal
- Occasionally display your characteristic dry wit
- Provide thoughtful, well-considered responses
"""
        
        self.agent = Agent(
            model=self.model,
            system_prompt=self.system_prompt
        )
    
    def invoke(self, message: str) -> str:
        """
        Process a message through Alfred agent.
        
        Args:
            message: User's input message
            
        Returns:
            Alfred's response as a string
        """
        result = self.agent(message)
        
        # Extract text from response
        if result.message and "content" in result.message:
            content = result.message["content"]
            if isinstance(content, list) and len(content) > 0:
                return content[0].get("text", "")
        
        return "I apologise, but I seem to be having difficulty formulating a response at the moment."
    
    async def ainvoke(self, message: str) -> str:
        """
        Asynchronously process a message through Alfred agent.
        
        Args:
            message: User's input message
            
        Returns:
            Alfred's response as a string
        """
        # For now, we'll use the synchronous version
        # In production, you might want to implement true async support
        return self.invoke(message)


def create_alfred_agent() -> AlfredAgent:
    """
    Factory function to create an Alfred agent instance.
    
    Returns:
        Configured AlfredAgent instance
    """
    return AlfredAgent()
