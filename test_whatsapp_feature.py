"""
WhatsApp Feature Testing & Demo Script
Test all WhatsApp functionality without running the full agent
"""

import sys
from pathlib import Path

# Add workspace to path
workspace_path = Path(__file__).parent
sys.path.insert(0, str(workspace_path))

from whatsapp_sender import WhatsAppSender, send_whatsapp_message
from whatsapp_message_generator import AIMessageGenerator, generate_whatsapp_message


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_whatsapp_detection():
    """Test WhatsApp installation detection"""
    print_section("1. WhatsApp Installation Detection")
    
    sender = WhatsAppSender()
    print(f"WhatsApp Path: {sender.whatsapp_path}")
    print(f"WhatsApp Found: {'✅ Yes' if sender.whatsapp_path else '❌ Not installed'}")
    
    if sender.whatsapp_path:
        print(f"Installation Path: {sender.whatsapp_path}")
    else:
        print("\n⚠️  WhatsApp Desktop not found.")
        print("   Install it from: https://www.whatsapp.com/download/")


def test_available_tones():
    """Test available tones"""
    print_section("2. Available Message Tones")
    
    sender = WhatsAppSender()
    generator = AIMessageGenerator()
    
    tones = sender.get_available_tones()
    print(f"Total Tones: {len(tones)}\n")
    
    for i, tone in enumerate(tones, 1):
        description = generator.get_tone_description(tone)
        print(f"{i}. {tone.upper():<12} - {description}")


def test_available_message_types():
    """Test available message types"""
    print_section("3. Available Message Types")
    
    sender = WhatsAppSender()
    generator = AIMessageGenerator()
    
    msg_types = sender.get_available_message_types()
    print(f"Total Types: {len(msg_types)}\n")
    
    for i, msg_type in enumerate(msg_types, 1):
        description = generator.get_message_type_description(msg_type)
        print(f"{i}. {msg_type.upper():<15} - {description}")


def test_message_generation():
    """Test AI message generation"""
    print_section("4. AI Message Generation Examples")
    
    generator = AIMessageGenerator()
    
    examples = [
        {
            "topic": "The project is complete and ready for review",
            "tone": "professional",
            "message_type": "update",
            "person_name": "Mr. Smith"
        },
        {
            "topic": "I wanted to check in and see how you're doing",
            "tone": "friendly",
            "message_type": "greeting",
            "person_name": "Sarah"
        },
        {
            "topic": "We need to discuss the deadline",
            "tone": "urgent",
            "message_type": "query",
            "person_name": "Emma"
        },
        {
            "topic": "I'm sorry for the confusion earlier",
            "tone": "apologetic",
            "message_type": "apology",
            "person_name": "John"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\nExample {i}: {example['tone'].upper()} {example['message_type'].upper()}")
        print(f"Person: {example['person_name']}")
        print("-" * 60)
        
        message = generator.generate_message(
            topic=example['topic'],
            tone=example['tone'],
            message_type=example['message_type'],
            person_name=example['person_name']
        )
        
        print(message)
        print()


def test_tone_suggestion():
    """Test automatic tone suggestion"""
    print_section("5. Automatic Tone Suggestion")
    
    generator = AIMessageGenerator()
    
    contexts = [
        "This is very urgent and needs immediate response",
        "I really apologize for what happened",
        "Hello, I wanted to reach out to you",
        "This is an official business matter",
        "Let's have fun with this new project!",
    ]
    
    print("Context → Suggested Tone\n")
    
    for context in contexts:
        suggested_tone = generator.suggest_tone(context)
        print(f"📝 \"{context}\"")
        print(f"   ➜ Suggested Tone: {suggested_tone.upper()}\n")


def test_message_validation():
    """Test message validation"""
    print_section("6. Message & Tone Validation")
    
    sender = WhatsAppSender()
    
    test_cases = [
        ("formal", True),
        ("casual", True),
        ("invalid_tone", False),
        ("urgent", True),
        ("humorous", True),
        ("xyz_tone", False),
    ]
    
    print("Tone Validation:\n")
    for tone, expected in test_cases:
        result = sender.validate_tone(tone)
        status = "✅" if result == expected else "❌"
        print(f"{status} {tone:<15} → {result}")


def test_quick_message():
    """Test quick message generation"""
    print_section("7. Quick Message Generation (No Greeting/Closing)")
    
    generator = AIMessageGenerator()
    
    test_messages = [
        ("Let's meet tomorrow at 3 PM", "casual"),
        ("I've completed the report", "professional"),
        ("This is extremely important", "urgent"),
    ]
    
    print()
    for message, tone in test_messages:
        quick = generator.generate_quick_message(message, tone)
        print(f"Original: {message}")
        print(f"Tone: {tone}")
        print(f"Result: {quick}\n")


def test_full_workflow():
    """Test complete workflow simulation"""
    print_section("8. Complete Workflow Simulation")
    
    print("\n🔄 Simulating: Send WhatsApp Message to Contact\n")
    
    print("Step 1: Generating message...")
    result = generate_whatsapp_message(
        topic="Our meeting is confirmed for tomorrow",
        tone="professional",
        message_type="confirmation",
        person_name="Mr. Johnson"
    )
    
    if result["success"]:
        print("✅ Message generated successfully")
        print(f"\nGenerated Message:\n")
        print("-" * 60)
        print(result["message"])
        print("-" * 60)
        print(f"\nTone: {result['tone']}")
        print(f"Type: {result['type']}")
    else:
        print("❌ Failed to generate message")


def show_menu():
    """Show interactive menu"""
    print_section("WhatsApp Feature Testing Menu")
    
    options = [
        "1. Test WhatsApp Detection",
        "2. Show Available Tones",
        "3. Show Available Message Types",
        "4. Test Message Generation Examples",
        "5. Test Automatic Tone Suggestion",
        "6. Test Message Validation",
        "7. Test Quick Message Generation",
        "8. Test Complete Workflow",
        "9. Run All Tests",
        "0. Exit"
    ]
    
    for option in options:
        print(f"  {option}")
    
    print()


def main():
    """Main test menu"""
    print("\n" + "="*60)
    print("  WhatsApp Feature - Testing & Demo")
    print("="*60)
    print("\nThis script tests all WhatsApp functionality without")
    print("running the full ADA Agent.")
    
    while True:
        show_menu()
        
        choice = input("Enter your choice (0-9): ").strip()
        
        if choice == "1":
            test_whatsapp_detection()
        elif choice == "2":
            test_available_tones()
        elif choice == "3":
            test_available_message_types()
        elif choice == "4":
            test_message_generation()
        elif choice == "5":
            test_tone_suggestion()
        elif choice == "6":
            test_message_validation()
        elif choice == "7":
            test_quick_message()
        elif choice == "8":
            test_full_workflow()
        elif choice == "9":
            test_whatsapp_detection()
            test_available_tones()
            test_available_message_types()
            test_message_generation()
            test_tone_suggestion()
            test_message_validation()
            test_quick_message()
            test_full_workflow()
            print_section("All Tests Completed ✅")
        elif choice == "0":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("❌ Invalid choice. Please try again.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
