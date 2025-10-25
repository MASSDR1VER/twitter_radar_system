from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, AsyncGenerator
import json
from .content import GeneratedContent
from .utils import build_grok_history, extract_image_prompts

if TYPE_CHECKING:
    from .client import Client


class GrokConversation:
    def __init__(self, client: Client, id: str, history: list | None = None) -> None:
        self._client = client
        self.id = id
        self.history = history if history is not None else []

    async def load_history(self):
        items = await self._client.get_grok_conversation_items(self.id)
        history = build_grok_history(items)
        self.history = history

    async def stream(
        self,
        message,
        file_attachments: list | None = None,
        model: str = 'stream',
        image_generation_count: int = 4
    ) -> AsyncGenerator[dict, None, None]:
        """
        Parameters
        ----------
        message : str
            The message that will be sent to generate a response.
        file_attachments : list | None, default=None
            A list of file attachments to send along with the message.
        model : str, default='stream'
            The model to use for generating the response.
        image_generation_count : int, default='4'
            The number of images to generate.
        """
        responses = deepcopy(self.history)
        if file_attachments is None:
            file_attachments = []
        responses.append({
            'message': message,
            'sender': 1,
            'promptSource': '',
            'fileAttachments': file_attachments
        })
        response_message = ''
        response_attachments = []
        async for res in self._client.grok_add_response(responses, self.id, model, image_generation_count):
            yield res
            if 'result' not in res:
                continue
            result = res['result']

            if 'message' in result:
                response_message += result['message']
            if 'imageAttachment' in result:
                image_attachment = result['imageAttachment']
                response_attachments.append({
                    'fileName': image_attachment['fileName'],
                    'mimeType': image_attachment['mimeType'],
                    'mediaId': image_attachment['mediaIdStr'],
                    'url': image_attachment['imageUrl']
                })
        if response_attachments:
            image_url = response_attachments[0]['url']
            image_bytes = await self._client.get_grok_image(image_url)
            prompt, _ = extract_image_prompts(image_bytes)
            response_message = f"I generated images with the prompt: '{prompt}'"

        self.history.append({
            'message': message,
            'sender': 1,
            'fileAttachments': file_attachments
        })
        self.history.append({
            'message': response_message,
            'sender': 2,
            'fileAttachments': response_attachments
        })
        
    async def generate(
        self, 
        message, 
        file_attachments: list | None = None,
        model: str = 'stream', 
        image_generation_count: int = 4,
        debug: bool = False
    ) -> GeneratedContent:
        """
        Generate a complete response without streaming.
        
        Parameters
        ----------
        message : str
            The message that will be sent to generate a response.
        file_attachments : list | None, default=None
            A list of file attachments to send along with the message.
        model : str, default='stream'
            The model to use for generating the response.
        image_generation_count : int, default=4
            The number of images to generate.
        debug : bool, default=False
            Whether to print debug information.
            
        Returns
        -------
        GeneratedContent
            An object containing the complete response including the message and any attachments.
        """
        # Collect all chunks from the stream
        chunks = []
        responses = deepcopy(self.history)
        if file_attachments is None:
            file_attachments = []
        
        # Add the user message to the history
        responses.append({
            'message': message,
            'sender': 1,
            'promptSource': '',
            'fileAttachments': file_attachments
        })
        
        # Collect all chunks and track message parts for debugging
        message_parts = []
        
        # Stream the response and collect all chunks
        async for chunk in self._client.grok_add_response(responses, self.id, model, image_generation_count):
            chunks.append(chunk)
            
            # Debug logging
            if debug:
                try:
                    print(f"Chunk: {json.dumps(chunk)}")
                    if 'result' in chunk and 'message' in chunk['result']:
                        message_parts.append(chunk['result']['message'])
                        print(f"Message part: {chunk['result']['message']}")
                except Exception as e:
                    print(f"Error logging chunk: {e}")
        
        # Generate content from collected chunks
        content = GeneratedContent(self._client, chunks)
        
        # Debug logging
        if debug:
            print(f"Total chunks: {len(chunks)}")
            print(f"Message parts: {message_parts}")
            print(f"Final message length: {len(content.message)}")
            print(f"First 100 chars: {content.message[:100]}")
            print(f"Last 100 chars: {content.message[-100:] if len(content.message) > 100 else content.message}")
            
        # Update conversation history
        self.history.append({
            'message': message,
            'sender': 1,
            'fileAttachments': file_attachments
        })
        
        self.history.append({
            'message': content.message,
            'sender': 2,
            'fileAttachments': [
                {
                    'fileName': attachment.file_name,
                    'mimeType': attachment.mime_type,
                    'mediaId': attachment.media_id,
                    'url': attachment.url
                }
                for attachment in content.attachments
            ]
        })
        
        return content

    def __repr__(self) -> str:
        return f'<GrokConversation id="{self.id}">'
