"""
Inicialización del módulo de endpoints API.
"""

from app.api.v1.endpoints import executive, control, fiscal, simulation

__all__ = ["executive", "control", "fiscal", "simulation"]
