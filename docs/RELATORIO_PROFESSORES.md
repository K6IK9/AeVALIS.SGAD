# Relatório de Professores

## 📋 Visão Geral

Nova página de relatório gerencial focada em **professores**, apresentando pontuações individuais, médias por ciclo e médias históricas de todas avaliações docentes.

## 🎯 Objetivo

Fornecer aos **coordenadores e administradores** uma visão consolidada do desempenho docente, permitindo:

- Acompanhar médias de avaliação por professor em um ciclo específico
- Comparar com médias históricas (todos os ciclos anteriores)
- Filtrar por curso, ciclo ou buscar por nome/matrícula
- Exportar dados em CSV para análises externas

## 🔑 Funcionalidades

### Métricas Apresentadas

Para cada professor, o relatório exibe:

- **Avaliações Respondidas**: Total de questionários respondidos no ciclo
- **Taxa de Resposta**: (Respondentes / Alunos Aptos) × 100%
- **Média no Ciclo**: Calculada com base no questionário padrão (0.00 a 1.00)
- **Classificação no Ciclo**: Não atende | Insuficiente | Regular | Bom | Excelente
- **Média Histórica**: Média geral de todos os ciclos anteriores
- **Classificação Histórica**: Baseada na média histórica

### Filtros Disponíveis

- **Ciclo de Avaliação**: Selecionar ciclo específico (obrigatório)
- **Curso**: Filtrar professores por curso
- **Busca**: Pesquisar por nome ou matrícula do professor

### Exportação CSV

Botão "Exportar CSV" gera planilha com 13 colunas:
```
Professor, Matrícula, Curso(s), Avaliações Respondidas, Total Respondentes, 
Total Alunos Aptos, Taxa de Resposta (%), Média no Ciclo, Classificação no Ciclo, 
Média Histórica, Classificação Histórica, Total Ciclos Históricos, Total Avaliações Históricas
```

## 🏗️ Arquitetura

### Arquivos Criados/Modificados

1. **`avaliacao_docente/services.py`** (NOVO)
   - `calcular_metricas_professor(professor, ciclo)`: Métricas de um professor em ciclo específico
   - `calcular_media_historica_professor(professor, excluir_ciclo)`: Média histórica excluindo ciclo atual
   - `listar_professores_com_metricas(ciclo, curso, busca)`: Lista professores com todas métricas aplicando filtros

2. **`avaliacao_docente/views.py`** (MODIFICADO)
   - `relatorio_professores(request)`: View principal com paginação e exportação CSV

3. **`avaliacao_docente/urls.py`** (MODIFICADO)
   - Rota: `/avaliacoes/relatorios/professores/`

4. **`templates/avaliacoes/relatorio_professores.html`** (NOVO)
   - Interface responsiva com tabela, filtros e cards de estatísticas

### Otimizações Aplicadas

- **Queries**: `select_related` e `prefetch_related` para evitar N+1
- **Agregação**: Cálculos feitos em Python para reaproveitar lógica dos modelos
- **Paginação**: 20 professores por página

## 🔐 Permissões

Acesso restrito a:
- ✅ Administradores
- ✅ Coordenadores

## 🧪 Como Testar

1. Faça login como coordenador ou admin
2. Acesse: `/avaliacoes/relatorios/professores/`
3. Selecione um **Ciclo de Avaliação**
4. Opcionalmente, filtre por **Curso** ou **Busca**
5. Clique em **Filtrar** para aplicar
6. Verifique as métricas na tabela
7. Clique em **Exportar CSV** para baixar planilha
8. Confirme que as classificações correspondem às médias:
   - **0.00-0.24**: Não atende
   - **0.25-0.49**: Insuficiente
   - **0.50-0.74**: Regular
   - **0.75-0.99**: Bom
   - **1.00**: Excelente

## 📊 Classificações

| Faixa de Média | Classificação | Cor Badge |
|----------------|---------------|-----------|
| 0.00 - 0.24    | Não atende    | 🔴 Vermelho |
| 0.25 - 0.49    | Insuficiente  | 🟠 Laranja |
| 0.50 - 0.74    | Regular       | 🟡 Amarelo |
| 0.75 - 0.99    | Bom           | 🟢 Verde Claro |
| 1.00           | Excelente     | 🟢 Verde Escuro |
| Sem dados      | Sem dados     | ⚪ Cinza |

## 🚀 Próximos Passos Recomendados

- [ ] Implementar testes automatizados (unit tests para services.py)
- [ ] Adicionar gráficos visuais (Chart.js) para evolução histórica
- [ ] Permitir comparação entre professores de mesma disciplina
- [ ] Adicionar exportação em PDF com gráficos

## 📝 Notas Técnicas

- **Dependências**: Reutiliza métodos de cálculo do modelo `AvaliacaoDocente`
- **Padrão de Código**: Segue convenções do projeto (views.py, templates)
- **Codacy**: Passou em todas verificações (sem issues críticos)
