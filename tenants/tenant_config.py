# -*- coding: utf-8 -*-
"""
Arquivo: tenant_config.py
Descrição: Módulo do sistema Belarmino Monteiro Advogado.
Autor: Equipe de Engenharia (Automated)
Data: 2025
"""

class TenantConfig:
    """
    Definição de TenantConfig.
    Componente essencial para a arquitetura do sistema.
    """
    def __init__(self, tenant_id: str, name: str, database_url: str):
        """
        Definição de __init__.
        Componente essencial para a arquitetura do sistema.
        """
        self.tenant_id = tenant_id
        self.name = name
        self.database_url = database_url

    def get_tenant_info(self) -> dict[str, str]:
        """
        Definição de get_tenant_info.
        Componente essencial para a arquitetura do sistema.
        """
        return {
            'tenant_id': self.tenant_id,
            'name': self.name,
            'database_url': self.database_url
        }
