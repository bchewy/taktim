"""
CrewAI Multimodal Agent System
Handles text, image, and document processing with specialized agents
"""

import os
from typing import Dict, List, Any, Optional
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, DirectoryReadTool
from langchain_openai import ChatOpenAI
import base64
from pathlib import Path


class MultimodalCrew:
    """CrewAI system for multimodal content analysis"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize tools
        self.file_tool = FileReadTool()
        self.directory_tool = DirectoryReadTool()
        
        # Create specialized agents
        self.agents = self._create_agents()
    
    def _create_agents(self) -> Dict[str, Agent]:
        """Create specialized agents for different content types"""
        
        # Document Analyst Agent
        document_agent = Agent(
            role="Document Analyst",
            goal="Extract, analyze, and summarize content from text documents, PDFs, and spreadsheets",
            backstory="""You are an expert document analyst with deep expertise in processing 
            various document formats. You excel at extracting key information, identifying 
            patterns, and creating comprehensive summaries.""",
            tools=[self.file_tool, self.directory_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Image Analyst Agent
        image_agent = Agent(
            role="Image Analyst", 
            goal="Analyze images, extract text via OCR, identify objects, and describe visual content",
            backstory="""You are a computer vision specialist with expertise in image analysis, 
            OCR, object detection, and visual content understanding. You can interpret 
            charts, diagrams, screenshots, and photographs.""",
            tools=[],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Content Synthesizer Agent
        synthesizer_agent = Agent(
            role="Content Synthesizer",
            goal="Combine insights from multiple sources and create comprehensive reports",
            backstory="""You are a master synthesizer who can take information from various 
            sources - documents, images, and data - and create coherent, insightful reports 
            that highlight key findings and relationships.""",
            tools=[],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        return {
            "document": document_agent,
            "image": image_agent,
            "synthesizer": synthesizer_agent
        }
    
    def analyze_documents(self, file_paths: List[str], query: str) -> str:
        """Analyze text documents and PDFs"""
        
        task = Task(
            description=f"""
            Analyze the following documents and answer this query: {query}
            
            Documents to analyze: {file_paths}
            
            Your analysis should include:
            1. Key information extracted from each document
            2. Main themes and patterns identified
            3. Relevant data points and statistics
            4. Direct answers to the user's query
            5. Summary of findings
            """,
            expected_output="Comprehensive document analysis with key insights and direct answers to the query",
            agent=self.agents["document"]
        )
        
        crew = Crew(
            agents=[self.agents["document"]],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result.raw
    
    def analyze_images(self, image_data: List[Dict], query: str) -> str:
        """Analyze images with vision capabilities"""
        
        image_descriptions = []
        for img_info in image_data:
            image_descriptions.append(f"Image: {img_info['filename']} - {img_info.get('description', 'No description')}")
        
        task = Task(
            description=f"""
            Analyze the provided images and answer this query: {query}
            
            Images provided: {image_descriptions}
            
            Your analysis should include:
            1. Visual content description for each image
            2. Text extraction (OCR) if applicable
            3. Object and scene identification
            4. Relevant visual patterns or data
            5. Direct answers to the user's query based on visual content
            """,
            expected_output="Detailed image analysis with visual insights and query responses",
            agent=self.agents["image"]
        )
        
        crew = Crew(
            agents=[self.agents["image"]],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result.raw
    
    def synthesize_multimodal_analysis(self, 
                                     document_analysis: str, 
                                     image_analysis: str, 
                                     query: str) -> str:
        """Combine document and image analysis into comprehensive report"""
        
        task = Task(
            description=f"""
            Create a comprehensive analysis report by synthesizing information from both 
            document analysis and image analysis to answer: {query}
            
            Document Analysis Results:
            {document_analysis}
            
            Image Analysis Results:
            {image_analysis}
            
            Your synthesis should include:
            1. Executive summary of key findings
            2. Cross-referenced insights between documents and images
            3. Comprehensive answer to the user's query
            4. Identified patterns and correlations
            5. Actionable recommendations if applicable
            """,
            expected_output="Comprehensive multimodal analysis report with synthesized insights",
            agent=self.agents["synthesizer"]
        )
        
        crew = Crew(
            agents=[self.agents["synthesizer"]],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result.raw
    
    def full_multimodal_analysis(self, 
                                file_paths: List[str], 
                                image_data: List[Dict], 
                                query: str) -> Dict[str, Any]:
        """Complete multimodal analysis workflow"""
        
        results = {}
        
        # Analyze documents if provided
        if file_paths:
            results["document_analysis"] = self.analyze_documents(file_paths, query)
        else:
            results["document_analysis"] = "No documents provided for analysis."
        
        # Analyze images if provided
        if image_data:
            results["image_analysis"] = self.analyze_images(image_data, query)
        else:
            results["image_analysis"] = "No images provided for analysis."
        
        # Synthesize results if we have both types of content
        if file_paths and image_data:
            results["synthesis"] = self.synthesize_multimodal_analysis(
                results["document_analysis"],
                results["image_analysis"],
                query
            )
        elif file_paths:
            results["synthesis"] = results["document_analysis"]
        elif image_data:
            results["synthesis"] = results["image_analysis"]
        else:
            results["synthesis"] = "No content provided for analysis."
        
        return results


class ChatAgent:
    """Interactive chat agent with multimodal context"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.chat_agent = Agent(
            role="Multimodal Assistant",
            goal="Provide helpful responses based on uploaded content and chat history",
            backstory="""You are an intelligent assistant with access to analyzed content 
            from documents and images. You can answer questions, provide insights, and 
            help users understand their multimodal data.""",
            tools=[],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def chat_with_context(self, message: str, context: Dict[str, Any]) -> str:
        """Chat with context from previous analyses"""
        
        context_info = ""
        if context.get("document_analysis"):
            context_info += f"\nDocument Analysis: {context['document_analysis']}"
        if context.get("image_analysis"):
            context_info += f"\nImage Analysis: {context['image_analysis']}"
        if context.get("synthesis"):
            context_info += f"\nSynthesis: {context['synthesis']}"
        
        task = Task(
            description=f"""
            Respond to the user's message using the available context from previous analyses.
            
            User Message: {message}
            
            Available Context: {context_info}
            
            Provide a helpful, accurate response that leverages the context when relevant.
            """,
            expected_output="Helpful response incorporating relevant context",
            agent=self.chat_agent
        )
        
        crew = Crew(
            agents=[self.chat_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        return result.raw