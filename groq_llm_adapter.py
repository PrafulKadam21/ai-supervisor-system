"""
Custom Groq LLM adapter for LiveKit Agents
This allows using Groq's FREE LLM API with LiveKit
"""
import os
from typing import List, Any
from groq import AsyncGroq
from livekit.agents import llm


class GroqLLM(llm.LLM):
    """Groq LLM implementation for LiveKit Agents"""
    
    def __init__(
        self,
        *,
        model: str = "llama-3.3-70b-versatile",
        api_key: str | None = None,
        temperature: float = 0.7,
    ):
        super().__init__()
        api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY must be set")
        
        self._client = AsyncGroq(api_key=api_key)
        self._model = model
        self._temperature = temperature
    
    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        **kwargs
    ) -> "LLMStream":
        """Generate chat completion using Groq"""
        return LLMStream(
            groq_llm=self,
            client=self._client,
            model=self._model,
            chat_ctx=chat_ctx,
            temperature=kwargs.get("temperature", self._temperature),
        )


class LLMStream(llm.LLMStream):
    """Groq LLM stream implementation"""
    
    def __init__(
        self,
        *,
        groq_llm: GroqLLM,
        client: AsyncGroq,
        model: str,
        chat_ctx: llm.ChatContext,
        temperature: float,
    ):
        # Try to initialize with the parameters that work
        try:
            # Try newer API first
            super().__init__(
                llm=groq_llm,
                chat_ctx=chat_ctx,
                tools=[],
                conn_options={},  # Use dict instead of class
            )
        except TypeError:
            # Fallback to simpler initialization
            super().__init__(
                llm=groq_llm,
                chat_ctx=chat_ctx,
            )
        
        self._client = client
        self._model = model
        self._temperature = temperature
    
    async def _run(self) -> None:
        """Run the streaming completion - REQUIRED abstract method"""
        # Convert LiveKit chat context to Groq format
        messages = []
        for msg in self._chat_ctx.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        try:
            # Stream response from Groq
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
                stream=True,
                max_tokens=1024,
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    
                    # Send content chunks using the correct method
                    self._event_ch.send_nowait(
                        llm.ChatChunk(
                            choices=[
                                llm.Choice(
                                    delta=llm.ChoiceDelta(
                                        content=content,
                                        role="assistant",
                                    )
                                )
                            ]
                        )
                    )
        
        except Exception as e:
            # Log error and re-raise
            print(f"Groq API error: {e}")
            raise