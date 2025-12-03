class TenantConfig:
    def __init__(self, tenant_id: str, name: str, database_url: str):
        self.tenant_id = tenant_id
        self.name = name
        self.database_url = database_url

    def get_tenant_info(self) -> dict[str, str]:
        return {
            'tenant_id': self.tenant_id,
            'name': self.name,
            'database_url': self.database_url
        }
