import sys
import json
import time
from backend.session import AssistantSession

def main():
    session = AssistantSession()
    
    # Simple standardized input loop
    # Explicitly flush stdout to ensure Electron receives events immediately
    sys.stdout.reconfigure(encoding='utf-8')
    
    print(json.dumps({"type": "status", "data": {"state": "Starting", "message": "Python backend started"}}), flush=True)

    try:
        session.initialize()
        session.start_audio()
        
        # Keep main thread alive and listening for commands if any
        while True:
            line = sys.stdin.readline()
            if not line:
                break
                
            try:
                cmd = json.loads(line)
                if cmd.get("command") == "stop":
                    session.stop()
                    break
                elif cmd.get("command") == "start":
                    session.start_audio()
                elif cmd.get("command") == "speak":
                    text = cmd.get("text")
                    if text:
                        session.tts.speak(text)
                elif cmd.get("command") == "set_language":
                    lang = cmd.get("lang", "ne")
                    session.set_language(lang)
            except json.JSONDecodeError:
                pass
                
    except KeyboardInterrupt:
        session.stop()
    except Exception as e:
        print(json.dumps({"type": "error", "data": {"message": str(e)}}), flush=True)
        session.stop()

if __name__ == "__main__":
    main()