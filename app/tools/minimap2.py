import subprocess
import os
from typing import List, Dict, Any
from .base import AlignmentTool

class Minimap2Tool(AlignmentTool):
    def index(self, fasta_path: str, output_path: str) -> bool:
        """Runs minimap2 -d."""
        cmd = ["minimap2", "-d", output_path, fasta_path]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def search(self, query_path: str, db_path: str, options: Dict[str, Any]) -> str:
        """Runs minimap2 and returns the path to the PAF output."""
        output_path = query_path + ".mm2.paf"
        
        # Use -c for PAF output with CIGAR
        cmd = ["minimap2", "-c", db_path, query_path]
        
        # Add presets if provided
        preset = options.get("preset")
        if preset:
            cmd.extend(["-x", preset])
            
        with open(output_path, "w") as f:
            subprocess.run(cmd, stdout=f, check=True)
            
        return output_path

    def parse_result(self, result_path: str) -> List[Dict[str, Any]]:
        """Parses Minimap2 PAF output."""
        if not os.path.exists(result_path):
            return []
            
        hits = []
        with open(result_path, 'r') as f:
            for line in f:
                cols = line.strip().split('\t')
                if len(cols) < 12:
                    continue
                
                # PAF format columns:
                # 0: Query seq name
                # 1: Query seq len
                # 2: Query start
                # 3: Query end
                # 4: Relative strand
                # 5: Target seq name
                # 6: Target seq len
                # 7: Target start
                # 8: Target end
                # 9: Number of residues match
                # 10: Alignment block length
                # 11: Mapping quality
                
                hits.append({
                    "query_name": cols[0],
                    "query_len": int(cols[1]),
                    "query_start": int(cols[2]),
                    "query_end": int(cols[3]),
                    "strand": cols[4],
                    "target_name": cols[5],
                    "target_len": int(cols[6]),
                    "target_start": int(cols[7]),
                    "target_end": int(cols[8]),
                    "matches": int(cols[9]),
                    "block_len": int(cols[10]),
                    "mapq": int(cols[11])
                })
        return hits
