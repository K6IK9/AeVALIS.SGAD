# 🚀 INSTRUÇÕES RÁPIDAS - Sistema de Avaliação Docente

## 📥 Acabou de baixar o projeto?

Execute este comando para configurar tudo automaticamente:

```bash
python setup_projeto.py
```

## 🔧 Configuração Manual (se necessário)

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar banco
python manage.py migrate

# 3. Configurar arquivos estáticos
python manage.py collectstatic --noinput

# 4. Executar
python manage.py runserver
```

## 🩺 Problema com imagens?

Execute o diagnóstico:

```bash
python diagnose_static.py
```

## 📋 Arquivos importantes:

- `setup_projeto.py` - Setup automático completo
- `diagnose_static.py` - Diagnóstico de problemas
- `STATIC_FILES_README.md` - Documentação detalhada
- `setup_static_files.py` - Configuração específica de assets

## 🌐 Após configurar:

```bash
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/

---

💡 **Dica**: Se ainda houver problemas, leia o arquivo `STATIC_FILES_README.md` para instruções detalhadas.
