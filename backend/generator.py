from .ssh import mkclient
import random
from os import getenv

words = [t.rstrip() for t in open("words.txt").readlines()]

mkname = lambda: "_".join(random.choice(words) for _ in range(2))
user = getenv("SSH_USER")

root = f"/home/{user}/Game"

def mktree(ip):
    client = mkclient(ip)
    
    # Generate directory structure
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
    
    # Determine which files to gzip
    # 2 gzipped, 3 not gzipped
    klad_gzip_flags = [True, True, False, False, False]
    random.shuffle(klad_gzip_flags)
    
    # Regular files about 50% chance of getting gzipped
    regular_gzip_flags = [random.choice([True, False]) for _ in range(25)]
    
    # Build the script
    script_lines = [
        "#!/bin/bash",
        # "set -e",
        f"rm -rf \"{root}\"",
        f"mkdir \"{root}\"",
        ""
    ]
    
    # Add directory creation commands
    for dir_path in dir_structure:
        script_lines.append(f"mkdir -p \"{dir_path}\"")
    
    script_lines.extend(["", ""])
    
    # Add regular file creation commands
    for dir_path, should_gzip in zip(regular_dirs, regular_gzip_flags):
        filename = mkname() + ".txt"
        full_path = f"{dir_path}/{filename}"
        
        if should_gzip:
            script_lines.append(f"cat > \"{full_path}\" << 'EOF'")
            for _ in range(20):
                line = ' '.join(random.choices(words, k=random.randint(3, 8)))
                script_lines.append(line)
            script_lines.append("EOF")
            script_lines.append(f"gzip \"{full_path}\"")
        else:
            script_lines.append(f"cat > \"{full_path}\" << 'EOF'")
            for _ in range(20):
                line = ' '.join(random.choices(words, k=random.randint(3, 8)))
                script_lines.append(line)
            script_lines.append("EOF")
        
        script_lines.append("")
    
    # Add klad file creation commands
    for (dir_path, pattern), should_gzip in zip(zip(klad_dirs, klad_patterns), klad_gzip_flags):
        filename = mkname() + ".txt"
        full_path = f"{dir_path}/{filename}"
        
        if should_gzip:
            script_lines.append(f"cat > \"{full_path}\" << 'EOF'")
            script_lines.append(pattern)
            for _ in range(19):
                line = ' '.join(random.choices(words, k=random.randint(3, 8)))
                script_lines.append(line)
            script_lines.append("EOF")
            script_lines.append(f"gzip \"{full_path}\"")
        else:
            script_lines.append(f"cat > \"{full_path}\" << 'EOF'")
            script_lines.append(pattern)
            for _ in range(19):
                line = ' '.join(random.choices(words, k=random.randint(3, 8)))
                script_lines.append(line)
            script_lines.append("EOF")
        
        script_lines.append("")
    
    # Join script lines
    script_content = "\n".join(script_lines)
    
    # Write and execute script on remote
    script_path = "/tmp/create_structure.sh"
    
    client.exec_command(f'cat > {script_path} << \"SCRIPT_EOF\"\n{script_content}\nSCRIPT_EOF')
    client.exec_command(f"chmod +x {script_path}")
    stdin, stdout, stderr = client.exec_command(script_path)
    print(stderr.read().decode())
    
    # Clean up
    client.exec_command(f"rm -f {script_path}")
    client.close()
    
    return klad_patterns
