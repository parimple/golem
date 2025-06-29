"""
Self-Assembly System - Modules that build themselves
"""
from .module_builder import (
    SelfAssemblingModule,
    ModuleFactory,
    ModuleCapabilities,
    ModuleHealth,
    EconomyModule,
    AIModule
)

__all__ = [
    'SelfAssemblingModule',
    'ModuleFactory',
    'ModuleCapabilities', 
    'ModuleHealth',
    'EconomyModule',
    'AIModule'
]