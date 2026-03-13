from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Any, Dict

# --- 1. SCHEMA DEI DATI IN USCITA ---
class ToolResult(BaseModel):
    """
    Formato standardizzato. L'LLM (DeepSeek) riceverà SEMPRE un oggetto fatto così,
    indipendentemente dal tool di rete utilizzato.
    """
    success: bool = Field(description="Indica se l'esecuzione ha avuto successo")
    data: Dict[str, Any] = Field(default_factory=dict, description="Dati estratti (es. porte aperte, CVE)")
    error_message: str = Field(default="", description="Dettagli dell'errore in caso di fallimento")


# --- 2. IL PATTERN STRATEGY (CLASSE ASTRATTA) ---
class BaseSecurityTool(ABC):
    """
    Interfaccia base. Tutti i futuri tool (Nmap, Dirb, ecc.) dovranno
    ereditare da questa classe e implementare questi metodi.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Il nome identificativo del tool per LangChain"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Descrizione vitale per far capire all'IA QUANDO usare questo tool"""
        pass

    @abstractmethod
    def execute(self, target: str, **kwargs) -> ToolResult:
        """
        Il motore del tool. Prende un target, esegue l'azione di rete
        e restituisce categoricamente un oggetto ToolResult.
        """
        pass