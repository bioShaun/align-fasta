from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AlignmentTool(ABC):
    @abstractmethod
    def index(self, fasta_path: str, output_path: str) -> bool:
        """Create index for the reference fasta."""
        pass
    
    @abstractmethod
    def search(self, query_path: str, db_path: str, options: Dict[str, Any]) -> str:
        """Run search/alignment and return path to result file."""
        pass
    
    @abstractmethod
    def parse_result(self, result_path: str) -> List[Dict[str, Any]]:
        """Parse result file into a structured list of hits."""
        pass
