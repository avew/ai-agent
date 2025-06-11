#!/usr/bin/env python3
"""
Test script for the new chunking functionality
"""
import os
import sys
from app import create_app
from app.services.embedding_service import EmbeddingService

def test_chunking():
    """Test the chunking functionality"""
    # Set environment variable to avoid OpenAI API calls during testing
    os.environ['OPENAI_API_KEY'] = 'test-key'
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create embedding service
            service = EmbeddingService()
            
            # Test text - simulating a longer document
            test_text = """
            Artificial Intelligence and Machine Learning Guide

            Introduction to Artificial Intelligence

            Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that work and react like humans. Some of the activities computers with artificial intelligence are designed for include:

            - Speech recognition
            - Learning
            - Planning  
            - Problem solving
            - Perception
            - Motion and manipulation

            Machine Learning Overview

            Machine Learning is a subset of AI that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. Machine learning focuses on the development of computer programs that can access data and use it to learn for themselves.

            Types of Machine Learning:

            1. Supervised Learning
               - Uses labeled training data
               - Examples: Classification, Regression
               - Algorithms: Linear Regression, Decision Trees, Random Forest

            2. Unsupervised Learning
               - Finds hidden patterns in data without labels
               - Examples: Clustering, Association
               - Algorithms: K-Means, Hierarchical Clustering

            3. Reinforcement Learning
               - Learns through interaction with environment
               - Uses rewards and penalties
               - Applications: Game playing, Robotics

            Deep Learning

            Deep Learning is a subset of machine learning in artificial intelligence that has networks capable of learning unsupervised from data that is unstructured or unlabeled. Also known as deep neural learning or deep neural networks.

            Key concepts:
            - Neural Networks
            - Backpropagation
            - Convolutional Neural Networks (CNN)
            - Recurrent Neural Networks (RNN)
            - Transformers
            """
            
            # Test token counting
            token_count = service.count_tokens(test_text)
            print(f"Total tokens in test text: {token_count}")
            
            # Test chunking
            chunks = service.create_chunks(test_text)
            print(f"\nCreated {len(chunks)} chunks:")
            
            total_chunk_tokens = 0
            for i, chunk in enumerate(chunks):
                print(f"\nChunk {i+1}:")
                print(f"  Token count: {chunk['token_count']}")
                print(f"  Character range: {chunk['start_char']}-{chunk['end_char']}")
                print(f"  Text preview: {chunk['text'][:100]}...")
                total_chunk_tokens += chunk['token_count']
            
            print(f"\nTotal tokens across all chunks: {total_chunk_tokens}")
            print(f"Original text tokens: {token_count}")
            
            # Test sentence splitting
            sentences = service._split_into_sentences(test_text)
            print(f"\nSplit into {len(sentences)} sentences")
            
            print("\n✅ Chunking functionality test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    success = test_chunking()
    sys.exit(0 if success else 1)
