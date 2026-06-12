import xml.etree.ElementTree as ET
import re

def parse_tdr_coordinates(tdr_path):
    """
    Parses a text-based TDR file to extract coordinate sequences.
    Modify the regex pattern depending on your exact TDR layout.
    """
    points = []
    
    # Example parser matching lines like: "X: 123.4, Y: 567.8" or "123.4 567.8"
    coord_pattern = re.compile(r'([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)')
    
    with open(input_tdr, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            match = coord_pattern.search(line)
            if match:
                x, y = float(match.group(1)), float(match.group(2))
                points.append((x, y))
                
    return points

def create_svg_from_points(points, svg_path):
    """
    Takes a list of (x, y) tuples and generates a structured SVG file.
    """
    if not points:
        print("No coordinate points found to convert.")
        return

    # Determine bounding box boundaries to set viewbox dynamically
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    width = max_x - min_x
    height = max_y - min_y
    
    # Padding around the geometry
    padding = max(width, height) * 0.05 if max(width, height) > 0 else 10
    
    # Setup SVG Root Element
    root = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'width': str(width + (padding * 2)),
        'height': str(height + (padding * 2)),
        'viewBox': f"{min_x - padding} {min_y - padding} {width + (padding * 2)} {height + (padding * 2)}"
    })
    
    # Build the path data string (M = Move to, L = Line to)
    path_data = f"M {points[0][0]} {points[0][1]} "
    for x, y in points[1:]:
        path_data += f"L {x} {y} "
        
    # Create the vector path element
    ET.SubElement(root, 'path', {
        'd': path_data.strip(),
        'stroke': 'black',
        'stroke-width': str(max(width, height) * 0.005 or 1),
        'fill': 'none'
    })
    
    # Write to file
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0) # Pretty-print the XML structure
    tree.write(svg_path, encoding='utf-8', xml_declaration=True)
    print(f"Successfully converted and saved to {svg_path}")

# --- Execution --- #generate SVG from TDR file.
if __name__ == "__main__":
    # Replace these paths with your real files
    # input_tdr = "simple_anonymous_particle_etching/simple_etch_out_fps.tdr"
    input_tdr = "simple_anonymous_particle_etching/advanced_etch_output_fps.tdr"
    output_svg = "output.svg"
    
    # Read, parse, and convert
    extracted_points = parse_tdr_coordinates(input_tdr)
    if extracted_points:
        create_svg_from_points(extracted_points, output_svg)