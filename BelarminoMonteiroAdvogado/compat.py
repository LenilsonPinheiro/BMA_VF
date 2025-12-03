# -*- coding: utf-8 -*-
"""
==============================================================================
Módulo de Compatibilidade (Shim) para SQLAlchemy
==============================================================================

Este módulo fornece um "shim" de compatibilidade para garantir que testes e
partes do código que dependem de APIs mais antigas do SQLAlchemy continuem a
funcionar sem quebrar.

Contexto:
---------
A função `engine.table_names()` foi descontinuada (deprecated) em versões mais
recentes do SQLAlchemy e posteriormente removida. Ela foi substituída pela
abordagem mais moderna `inspect(engine).get_table_names()`.

Implementação:
--------------
Este módulo é importado no início do ciclo de vida da aplicação (em
`__init__.py`) para adicionar dinamicamente o método `table_names()` de volta
à classe `sqlalchemy.engine.Engine`, caso ele não exista.

O método injetado (`_engine_table_names`) tenta usar a API moderna (`inspect`)
primeiro e, como fallback, tenta métodos do dialeto específico, garantindo
máxima compatibilidade.

Este procedimento é conhecido como "monkey patching" e é usado aqui de
forma controlada para manter a retrocompatibilidade com testes legados.
"""
from sqlalchemy import inspect
import sqlalchemy.engine


def _engine_table_names(self):
    """
    Implementação do método legado `table_names()` para o SQLAlchemy Engine.
    Tenta obter os nomes das tabelas usando a API moderna e, em caso de falha,
    recorre a métodos de fallback.
    """
    try:
        # Abordagem moderna e preferencial
        return inspect(self).get_table_names()
    except Exception:
        # Fallback para dialetos que podem ter implementações mais antigas.
        # Uma exceção genérica é usada aqui para garantir que a aplicação
        # não quebre, mesmo com versões inesperadas do SQLAlchemy ou dialetos.
        try:
            return list(self.dialect.get_table_names(self))
        except Exception:
            # Retorna uma lista vazia como último recurso para evitar falhas.
            return []


# Anexa o método de compatibilidade à classe Engine somente se ele não existir.
# Isso evita sobrescrever o método se ele estiver presente em versões futuras
# ou se outro patch já o tiver adicionado.
if not hasattr(sqlalchemy.engine.Engine, 'table_names'):
    setattr(sqlalchemy.engine.Engine, 'table_names', _engine_table_names)
