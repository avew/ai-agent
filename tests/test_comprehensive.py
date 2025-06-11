#!/usr/bin/env python3
"""
Comprehensive test for document chunking with embeddings
"""
import os
import tempfile
from app import create_app
from app.services.document_service import DocumentService

def test_document_upload_with_chunking():
    """Test complete document upload flow with chunking"""
    
    # Create a longer test document to ensure chunking happens
    long_content = """
    # Comprehensive Guide to Artificial Intelligence and Machine Learning

    ## Chapter 1: Introduction to Artificial Intelligence

    Artificial Intelligence (AI) represents one of the most significant technological advances of our time. It encompasses the development of computer systems that can perform tasks typically requiring human intelligence. These tasks include visual perception, speech recognition, decision-making, and language translation.

    The field of AI has evolved dramatically since its inception in the 1950s. Early pioneers like Alan Turing laid the groundwork with concepts such as the Turing Test, which proposed a method for determining whether a machine can exhibit intelligent behavior equivalent to, or indistinguishable from, that of a human.

    Modern AI systems are built on sophisticated algorithms and vast amounts of data. They can learn from experience, adapt to new inputs, and perform human-like tasks with remarkable accuracy. This has led to breakthrough applications in healthcare, finance, transportation, and many other sectors.

    ## Chapter 2: Machine Learning Fundamentals

    Machine Learning (ML) is a subset of artificial intelligence that focuses on the development of algorithms that can learn and make decisions from data without being explicitly programmed for every scenario. The core principle of machine learning is to enable computers to learn automatically without human intervention or assistance.

    ### 2.1 Types of Machine Learning

    There are three primary types of machine learning:

    **Supervised Learning**: This approach uses labeled training data to learn a mapping function from input variables to output variables. Common applications include email spam detection, image classification, and medical diagnosis. Popular algorithms include linear regression, decision trees, random forests, and support vector machines.

    **Unsupervised Learning**: This method finds hidden patterns in data without the use of labeled examples. It's particularly useful for exploratory data analysis, customer segmentation, and anomaly detection. Key techniques include clustering algorithms like K-means, hierarchical clustering, and dimensionality reduction methods such as Principal Component Analysis (PCA).

    **Reinforcement Learning**: This paradigm involves an agent learning to make decisions by taking actions in an environment to maximize cumulative reward. It's the foundation of game-playing AI systems, robotics control, and autonomous vehicle navigation. Notable algorithms include Q-learning, policy gradients, and actor-critic methods.

    ### 2.2 The Machine Learning Pipeline

    A typical machine learning project follows several key stages:

    1. **Data Collection**: Gathering relevant, high-quality data from various sources
    2. **Data Preprocessing**: Cleaning, transforming, and preparing data for analysis
    3. **Feature Engineering**: Selecting and creating relevant features that help the model learn
    4. **Model Selection**: Choosing appropriate algorithms based on the problem type and data characteristics
    5. **Training**: Teaching the model using historical data
    6. **Evaluation**: Assessing model performance using metrics like accuracy, precision, recall, and F1-score
    7. **Deployment**: Implementing the model in a production environment
    8. **Monitoring**: Continuously tracking model performance and updating as needed

    ## Chapter 3: Deep Learning and Neural Networks

    Deep Learning is a specialized subset of machine learning that uses artificial neural networks with multiple layers to model and understand complex patterns in data. These networks are inspired by the structure and function of the human brain, with interconnected nodes (neurons) that process and transmit information.

    ### 3.1 Neural Network Architecture

    A neural network consists of layers of interconnected nodes:
    - **Input Layer**: Receives raw data
    - **Hidden Layers**: Process information through weighted connections and activation functions
    - **Output Layer**: Produces final predictions or classifications

    The power of deep learning comes from its ability to automatically learn hierarchical representations of data, from simple features in early layers to complex patterns in deeper layers.

    ### 3.2 Popular Deep Learning Architectures

    **Convolutional Neural Networks (CNNs)**: Designed for processing grid-like data such as images. They use convolutional layers to detect local features and are highly effective for computer vision tasks.

    **Recurrent Neural Networks (RNNs)**: Specialized for sequential data processing. Variants like LSTM (Long Short-Term Memory) and GRU (Gated Recurrent Unit) can handle long-term dependencies in data.

    **Transformers**: Revolutionary architecture that has transformed natural language processing. The attention mechanism allows the model to focus on relevant parts of the input sequence, leading to breakthroughs in language understanding and generation.

    ## Chapter 4: Applications and Real-World Impact

    AI and ML technologies have found applications across numerous industries:

    ### Healthcare
    - Medical image analysis for disease detection
    - Drug discovery and development
    - Personalized treatment recommendations
    - Electronic health record analysis
    - Predictive analytics for patient outcomes

    ### Finance
    - Algorithmic trading strategies
    - Fraud detection and prevention
    - Credit scoring and risk assessment
    - Robo-advisors for investment management
    - Regulatory compliance monitoring

    ### Transportation
    - Autonomous vehicle development
    - Traffic optimization systems
    - Predictive maintenance for fleets
    - Route planning and logistics
    - Smart city infrastructure

    ### Technology
    - Search engine optimization
    - Recommendation systems
    - Natural language processing
    - Computer vision applications
    - Voice assistants and chatbots

    ## Chapter 5: Ethical Considerations and Future Directions

    As AI systems become more prevalent and powerful, it's crucial to address ethical considerations:

    ### 5.1 Bias and Fairness
    AI systems can perpetuate or amplify existing biases present in training data. Ensuring fairness across different demographic groups requires careful attention to data collection, algorithm design, and ongoing monitoring.

    ### 5.2 Privacy and Security
    The vast amounts of data required for AI systems raise important privacy concerns. Techniques like differential privacy and federated learning are being developed to protect individual privacy while enabling AI advancement.

    ### 5.3 Transparency and Explainability
    Many AI systems, particularly deep learning models, operate as "black boxes." Developing interpretable AI that can explain its decision-making process is crucial for trust and accountability.

    ### 5.4 Future Trends
    The field continues to evolve rapidly with emerging trends including:
    - Artificial General Intelligence (AGI) research
    - Quantum machine learning
    - Edge AI and distributed computing
    - Sustainable AI with reduced environmental impact
    - Human-AI collaboration frameworks

    ## Conclusion

    Artificial Intelligence and Machine Learning represent transformative technologies that are reshaping our world. From healthcare breakthroughs to autonomous systems, these technologies offer unprecedented opportunities to solve complex problems and improve human life.

    However, with great power comes great responsibility. As we continue to advance these technologies, we must remain vigilant about their ethical implications and work to ensure they benefit all of humanity. The future of AI depends not just on technical innovation, but on our collective wisdom in developing and deploying these powerful tools responsibly.

    Success in the AI field requires continuous learning, ethical awareness, and a commitment to creating technology that serves the greater good. As we stand on the brink of even more revolutionary developments, the importance of thoughtful, responsible AI development cannot be overstated.
    """
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(long_content)
                temp_file_path = f.name
            
            # Test document service
            document_service = DocumentService()
            
            # Simulate file upload
            with open(temp_file_path, 'rb') as file:
                result = document_service.upload_document(file, "ai_comprehensive_guide.txt")
            
            if result['success']:
                document_id = result['document_id']
                print(f"✅ Document uploaded successfully with ID: {document_id}")
                
                # Get document chunks
                chunks = document_service.get_document_chunks(document_id)
                print(f"📄 Document was split into {len(chunks)} chunks:")
                
                total_tokens = 0
                for chunk in chunks:
                    print(f"  Chunk {chunk.chunk_index + 1}: {chunk.token_count} tokens")
                    total_tokens += chunk.token_count
                
                print(f"📊 Total tokens across all chunks: {total_tokens}")
                
                # Clean up
                os.unlink(temp_file_path)
                
                return True
            else:
                print(f"❌ Upload failed: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🔧 Testing document upload with chunking...")
    # Note: This test requires a valid OpenAI API key and database connection
    # It will make actual API calls to generate embeddings
    success = test_document_upload_with_chunking()
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
