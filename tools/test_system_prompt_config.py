#!/usr/bin/env python3
"""
Test script untuk memverifikasi system prompt configuration.
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

#!/usr/bin/env python3
"""
Test script untuk memverifikasi system and user prompt configuration.
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def test_prompt_config():
    """Test system and user prompt configuration."""
    print("=== System and User Prompt Configuration Test ===\n")
    
    # Test 1: Check environment variables
    system_prompt_env = os.getenv('SYSTEM_PROMPT')
    user_template_env = os.getenv('USER_PROMPT_TEMPLATE')
    
    print(f"1. Environment Variables:")
    if system_prompt_env:
        print(f"   ✓ SYSTEM_PROMPT: {system_prompt_env[:60]}{'...' if len(system_prompt_env) > 60 else ''}")
    else:
        print("   ⚠ SYSTEM_PROMPT: Not found (will use default)")
    
    if user_template_env:
        print(f"   ✓ USER_PROMPT_TEMPLATE: {user_template_env[:60]}{'...' if len(user_template_env) > 60 else ''}")
    else:
        print("   ⚠ USER_PROMPT_TEMPLATE: Not found (will use default)")
    
    print()
    
    # Test 2: Check config loading
    try:
        from app.config import Config
        config_system = Config.SYSTEM_PROMPT
        config_user = Config.USER_PROMPT_TEMPLATE
        
        print(f"2. Config Loading:")
        print(f"   ✓ SYSTEM_PROMPT: {config_system[:60]}{'...' if len(config_system) > 60 else ''}")
        print(f"   ✓ USER_PROMPT_TEMPLATE: {config_user[:60]}{'...' if len(config_user) > 60 else ''}")
        
        # Validate user template has required placeholders
        if '{context}' in config_user and '{query}' in config_user:
            print("   ✓ User template has required placeholders")
        else:
            print("   ⚠ User template missing required placeholders")
        
    except Exception as e:
        print(f"   ✗ Error loading config: {e}")
        return False
    
    print()
    
    # Test 3: Test in Flask app context
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.services.search_service import SearchService
            search_service = SearchService()
            
            service_system = search_service.system_prompt
            service_user = search_service.user_prompt_template
            
            print(f"3. SearchService Loading:")
            print(f"   ✓ system_prompt: {service_system[:60]}{'...' if len(service_system) > 60 else ''}")
            print(f"   ✓ user_prompt_template: {service_user[:60]}{'...' if len(service_user) > 60 else ''}")
            
            # Test template formatting
            try:
                test_context = "Test context here"
                test_query = "Test query here"
                formatted_prompt = service_user.format(context=test_context, query=test_query)
                print("   ✓ Template formatting successful")
                print(f"   Sample formatted: {formatted_prompt[:80]}{'...' if len(formatted_prompt) > 80 else ''}")
            except Exception as e:
                print(f"   ✗ Template formatting error: {e}")
                
    except Exception as e:
        print(f"   ⚠ Could not test SearchService: {e}")
    
    print("\n=== Test Complete ===")
    return True

def demo_custom_prompts():
    """Demonstrate different system and user prompt examples."""
    print("\n=== Custom Prompt Combinations Examples ===\n")
    
    examples = [
        {
            "name": "Business Consultant",
            "system": "Anda adalah konsultan bisnis profesional. Berikan analisis strategis dan rekomendasi bisnis berdasarkan data perusahaan.",
            "user": "Data dan informasi perusahaan:\\n{context}\\n\\nPertanyaan strategis: {query}\\n\\nBerikan analisis profesional dengan rekomendasi yang dapat diimplementasikan."
        },
        {
            "name": "Technical Support",
            "system": "You are a senior technical support specialist. Provide clear, step-by-step technical solutions.",
            "user": "Technical Documentation:\\n{context}\\n\\nTechnical Issue: {query}\\n\\nProvide step-by-step solution with troubleshooting steps."
        },
        {
            "name": "Educational Tutor",
            "system": "Kamu adalah tutor yang sabar dan komunikatif. Jelaskan konsep dengan cara yang mudah dipahami.",
            "user": "Materi pembelajaran:\\n{context}\\n\\nPertanyaan siswa: {query}\\n\\nJelaskan dengan cara yang mudah dipahami dan berikan contoh praktis."
        },
        {
            "name": "Research Assistant",
            "system": "You are a research analyst with expertise in academic literature. Provide evidence-based analysis.",
            "user": "Research Papers:\\n{context}\\n\\nResearch Question: {query}\\n\\nProvide comprehensive analysis with citations and evidence-based conclusions."
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['name']}:")
        print(f"   SYSTEM_PROMPT=\"{example['system']}\"")
        print(f"   USER_PROMPT_TEMPLATE=\"{example['user']}\"")
        print()
    
    print("To use any combination, add both variables to your .env file and restart the application.")

if __name__ == "__main__":
    success = test_prompt_config()
    
    if success:
        demo_custom_prompts()
