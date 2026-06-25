import os
import sys
import re
import subprocess

def convert_tdr_to_ascii_via_sentaurus(tdr_path, ascii_path):
    """
    Tries to run Sentaurus tdr2ascii utility to convert binary TDR to ASCII.
    """
    print(f"Attempting to convert binary {tdr_path} to ASCII format...")
    # Check if tdr2ascii or similar Sentaurus tool is available locally
    try:
        # standard Sentaurus utility command
        cmd = ["tdr2ascii", tdr_path, ascii_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Successfully converted TDR to ASCII via Sentaurus tdr2ascii.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Alternative: use sprocess script to load and save as ASCII
        script_content = f"""
        math dimension=3
        struct tdr="{tdr_path}"
        struct tdr="{ascii_path}" ascii
        """
        temp_cmd = "temp_convert.cmd"
        with open(temp_cmd, "w") as f:
            f.write(script_content)
        try:
            subprocess.run(["sprocess", temp_cmd], capture_output=True, check=True)
            os.remove(temp_cmd)
            print("Successfully converted TDR to ASCII via sprocess script.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            if os.path.exists(temp_cmd):
                os.remove(temp_cmd)
            print("[Warning] Sentaurus utilities (tdr2ascii/sprocess) not found in local PATH. Assumed file is already ASCII.")
            return False

def parse_dfise_ascii(ascii_path):
    """
    Parses a DF-ISE ASCII file to extract vertices and elements.
    """
    print(f"Parsing ASCII DF-ISE file: {ascii_path}")
    if not os.path.exists(ascii_path):
        print(f"File not found: {ascii_path}")
        return None, None
        
    with open(ascii_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # 1. Parse Vertices
    vertices = []
    vertex_match = re.search(r'Vertices\s*\((.*?)\)', content, re.DOTALL)
    if vertex_match:
        coords_str = vertex_match.group(1).strip()
        # Find all coordinate floats
        floats = [float(val) for val in re.findall(r'[-+]?\d+\.?\d*[eE]?[+-]?\d*', coords_str)]
        # Group into 3D coordinates (X, Y, Z)
        for i in range(0, len(floats), 3):
            if i + 2 < len(floats):
                vertices.append((floats[i], floats[i+1], floats[i+2]))
    print(f"Extracted {len(vertices)} vertices.")
    
    # 2. Parse Elements (simplices/triangles/tetrahedrons)
    elements = []
    # Elements section typically looks like: Elements ( [type] [node_indices] )
    elem_match = re.search(r'Elements\s*\((.*?)\)', content, re.DOTALL)
    if elem_match:
        elem_str = elem_match.group(1).strip()
        # Parse lines containing elements
        lines = elem_str.split('\n')
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 4:
                try:
                    # In DF-ISE, element type is often the first number (e.g. 2=triangle, 5=tetrahedron)
                    elem_type = int(parts[0])
                    # Node indices are integers starting after type
                    nodes = [int(p) for p in parts[1:] if p.isdigit()]
                    elements.append((elem_type, nodes))
                except ValueError:
                    continue
    print(f"Extracted {len(elements)} elements.")
    return vertices, elements

def write_vtk_unstructured_grid(vertices, elements, vtk_path):
    """
    Writes extracted mesh data into a legacy VTK Unstructured Grid file format.
    """
    if not vertices:
        print("No vertices to write.")
        return
        
    print(f"Writing VTK unstructured grid to: {vtk_path}")
    with open(vtk_path, 'w') as f:
        # Header
        f.write("# vtk DataFile Version 3.0\n")
        f.write("Sentaurus Process TDR to VTK Mesh\n")
        f.write("ASCII\n")
        f.write("DATASET UNSTRUCTURED_GRID\n\n")
        
        # Points
        f.write(f"POINTS {len(vertices)} float\n")
        for v in vertices:
            f.write(f"{v[0]} {v[1]} {v[2]}\n")
        f.write("\n")
        
        # Cell count and cell list size calculation
        # Each cell has: number of nodes + list of node indices
        total_cells = len(elements)
        cell_list_size = sum(len(nodes) + 1 for _, nodes in elements)
        
        f.write(f"CELLS {total_cells} {cell_list_size}\n")
        for _, nodes in elements:
            f.write(f"{len(nodes)} " + " ".join(str(n) for n in nodes) + "\n")
        f.write("\n")
        
        # Cell types mapping DF-ISE type to VTK type
        # DF-ISE elements: 2 = Triangle, 5 = Tetrahedron, etc.
        # VTK cell types: 5 = Triangle, 10 = Tetrahedron
        f.write(f"CELL_TYPES {total_cells}\n")
        for elem_type, _ in elements:
            # Map types
            if elem_type == 2:
                vtk_type = 5  # VTK_TRIANGLE
            elif elem_type == 5:
                vtk_type = 10 # VTK_TETRA
            else:
                vtk_type = 5  # Fallback to triangle
            f.write(f"{vtk_type}\n")
            
    print(f"Successfully created VTK file: {vtk_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python tdr2vtk.py <input_tdr_file> [output_vtk_file]")
        return
        
    input_tdr = sys.argv[1]
    output_vtk = sys.argv[2] if len(sys.argv) > 2 else input_tdr.replace(".tdr", ".vtk")
    ascii_path = input_tdr.replace(".tdr", "_ascii.tdr")
    
    # Try converting to ASCII
    has_sentaurus = convert_tdr_to_ascii_via_sentaurus(input_tdr, ascii_path)
    
    # If Sentaurus is not available locally, we check if there's already an ASCII file
    target_ascii = ascii_path if has_sentaurus else input_tdr
    
    vertices, elements = parse_dfise_ascii(target_ascii)
    if vertices:
        write_vtk_unstructured_grid(vertices, elements, output_vtk)
        
    # Cleanup temporary ASCII file if generated
    if has_sentaurus and os.path.exists(ascii_path):
        os.remove(ascii_path)

if __name__ == "__main__":
    main()
