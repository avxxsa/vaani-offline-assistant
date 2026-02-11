# actions/search_actions.py
import os
import platform
from pathlib import Path

def local_file_search(query: str, search_path=None, max_results=10):
    """
    Search for files by name in the local system.
    
    Args:
        query: The search term (file name or part of it)
        search_path: Directory to search in (defaults to user's home directory)
        max_results: Maximum number of results to return
    
    Returns:
        Dictionary with success status and list of found files
    """
    if search_path is None:
        # Default to user's home directory
        search_path = str(Path.home())
    
    results = []
    query_lower = query.lower()
    
    try:
        # Walk through the directory tree
        for root, dirs, files in os.walk(search_path):
            # Skip hidden directories and system folders
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
            
            for file in files:
                if query_lower in file.lower():
                    full_path = os.path.join(root, file)
                    results.append({
                        "name": file,
                        "path": full_path,
                        "size": os.path.getsize(full_path)
                    })
                    
                    if len(results) >= max_results:
                        return {
                            "success": True,
                            "query": query,
                            "results": results,
                            "count": len(results)
                        }
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }

def search_in_common_locations(query: str):
    """
    Search for files in common user locations (Desktop, Documents, Downloads).
    Faster than searching entire home directory.
    """
    system = platform.system()
    home = Path.home()
    
    # Common folders to search
    if system == "Windows":
        common_paths = [
            home / "Desktop",
            home / "Documents",
            home / "Downloads",
            home / "Pictures",
        ]
    else:  # Linux/Mac
        common_paths = [
            home / "Desktop",
            home / "Documents",
            home / "Downloads",
            home / "Pictures",
        ]
    
    all_results = []
    query_lower = query.lower()
    
    for path in common_paths:
        if path.exists():
            try:
                for item in path.rglob("*"):
                    if item.is_file() and query_lower in item.name.lower():
                        all_results.append({
                            "name": item.name,
                            "path": str(item),
                            "location": path.name,
                            "size": item.stat().st_size
                        })
            except PermissionError:
                continue
    
    return {
        "success": True,
        "query": query,
        "results": all_results[:10],  
        "count": len(all_results)
    }

def web_search(query: str):
    """
    Open a web search in the default browser.
    """
    import webbrowser
    
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return {
            "success": True,
            "query": query,
            "action": "Opened web search in browser"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }