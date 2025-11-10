from ssh import mkclient
import random

words = [t.rstrip() for t in open("words.txt").readlines()]

mkname = lambda: "_".join(random.sample(words, 2))
root = "/home/game/Game"

import random

words = [t.rstrip() for t in open("words.txt").readlines()]

mkname = lambda: "_".join(random.choice(words) for _ in range(2))
root = "/home/game/Game"

import random

words = [t.rstrip() for t in open("words.txt").readlines()]

mkname = lambda: "_".join(random.choice(words) for _ in range(2))
root = "/home/game/Game"

import random

words = [t.rstrip() for t in open("words.txt").readlines()]

mkname = lambda: "_".join(random.choice(words) for _ in range(2))
root = "/home/game/Game"

def mktree(ip):
    client = mkclient(ip)
    
    # Generate directory structure in Python
    dir_structure = []
    for i in range(5):
        dir1 = mkname()
        dir_structure.append(f"{root}/{dir1}")
        for j in range(5):
            dir2 = mkname()
            dir_structure.append(f"{root}/{dir1}/{dir2}")
            for k in range(5):
                dir3 = mkname()
                dir_structure.append(f"{root}/{dir1}/{dir2}/{dir3}")
    
    # Generate klad patterns
    klad_patterns = []
    for _ in range(5):
        three_words = ' '.join(random.sample(words, 3))
        klad_patterns.append(f"klad:{three_words}")
    
    # Select directories for files
    selected_dirs = random.sample(dir_structure, 30)
    klad_dirs = selected_dirs[:5]
    regular_dirs = selected_dirs[5:]
    
    # Choose 2 random klad files to compress
    klad_to_compress = random.sample(range(5), 2)
    
    # Build the script
    script_lines = [
        "#!/bin/bash",
        "set -e",  # Exit on error
        f"rm -rf \"{root}\"",
        "",
        "# Create directory structure"
    ]
    
    # Add directory creation commands
    for dir_path in dir_structure:
        script_lines.append(f"mkdir -p \"{dir_path}\"")
    
    script_lines.extend(["", "# Create regular files"])
    
    # Add regular file creation commands
    for i, dir_path in enumerate(regular_dirs):
        filename = mkname() + ".txt"
        script_lines.append(f"# Regular file {i+1}")
        script_lines.append(f"cat > \"{dir_path}/{filename}\" << 'EOF'")
        # Generate 20 lines of random garbage
        for _ in range(20):
            line = ' '.join(random.choices(words, k=random.randint(3, 8)))
            script_lines.append(line)
        script_lines.append("EOF")
        script_lines.append("")
    
    script_lines.append("# Create klad files")
    
    # Add klad file creation commands
    for i, (dir_path, pattern) in enumerate(zip(klad_dirs, klad_patterns)):
        filename = mkname() + ".txt"
        full_path = f"{dir_path}/{filename}"
        is_compressed = i in klad_to_compress
        
        script_lines.append(f"# Klad file {i+1}" + (" (compressed)" if is_compressed else ""))
        script_lines.append(f"cat > \"{full_path}\" << 'EOF'")
        script_lines.append(pattern)
        # Generate 19 more lines of random garbage
        for _ in range(19):
            line = ' '.join(random.choices(words, k=random.randint(3, 8)))
            script_lines.append(line)
        script_lines.append("EOF")
        
        # Compress if selected
        if is_compressed:
            script_lines.append(f"gzip \"{full_path}\"")
        
        script_lines.append("")
    
    # Join script lines
    script_content = "\n".join(script_lines)
    
    # Write and execute script on remote
    script_path = "/tmp/create_structure.sh"
    
    # Use printf to handle special characters and write script
    client.exec_command(f'cat > {script_path} << \"SCRIPT_EOF\"\n{script_content}\nSCRIPT_EOF')
    
    # Make executable and run
    client.exec_command(f"chmod +x {script_path}")
    stdin, stdout, stderr = client.exec_command(script_path)
    
    # Clean up script
    client.exec_command(f"rm -f {script_path}")
    client.close()
    print(f"Generated for {ip}, {klad_patterns}")
    return klad_patterns