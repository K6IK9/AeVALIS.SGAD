CREATE TABLE perfil_aluno (
    id SERIAL PRIMARY KEY,
    data_criacao TIMESTAMPTZ NOT NULL,
    data_atualizacao TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER UNIQUE REFERENCES auth_user (id) ON DELETE CASCADE,
    nome_completo VARCHAR(300) NOT NULL,
    matricula VARCHAR(20) UNIQUE,
    email VARCHAR(300) UNIQUE
);

CREATE TABLE perfil_professor (
    id SERIAL PRIMARY KEY,
    data_criacao TIMESTAMPTZ NOT NULL,
    data_atualizacao TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER UNIQUE REFERENCES auth_user (id) ON DELETE CASCADE,
    nome_completo VARCHAR(300) NOT NULL,
    email VARCHAR(300) UNIQUE
);

CREATE TABLE curso (
    id SERIAL PRIMARY KEY,
    data_criacao TIMESTAMPTZ NOT NULL,
    data_atualizacao TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    nome VARCHAR(100) NOT NULL UNIQUE,
    coordenador_id INTEGER UNIQUE REFERENCES perfil_professor (id)
);

CREATE TABLE disciplina (
    id SERIAL PRIMARY KEY,
    data_criacao TIMESTAMPTZ NOT NULL,
    data_atualizacao TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    nome VARCHAR(150) NOT NULL,
    curso_id INTEGER NOT NULL REFERENCES curso (id)
);

CREATE TABLE turma (
    id SERIAL PRIMARY KEY,
    data_criacao TIMESTAMPTZ NOT NULL,
    data_atualizacao TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    disciplina_id INTEGER NOT NULL REFERENCES disciplina (id),
    professor_id INTEGER NOT NULL REFERENCES perfil_professor (id)
);

CREATE TABLE matricula (
    id SERIAL PRIMARY KEY,
    data_criacao TIMESTAMPTZ NOT NULL,
    data_atualizacao TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL DEFAULT 'ativo',
    aluno_id INTEGER NOT NULL REFERENCES perfil_aluno (id),
    turma_id INTEGER NOT NULL REFERENCES turma (id),
    UNIQUE (aluno_id, turma_id)
);

CREATE TABLE questionario (
    id SERIAL PRIMARY KEY,
    data_criacao TIMESTAMPTZ NOT NULL,
    data_atualizacao TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE avaliacao_pergunta (
    id SERIAL PRIMARY KEY,
    data_criacao TIMESTAMPTZ NOT NULL,
    data_atualizacao TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    questionario_id INTEGER NOT NULL REFERENCES questionario (id),
    texto TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    ordem INTEGER NOT NULL,
    obrigatoria BOOLEAN NOT NULL DEFAULT TRUE,
    opcoes JSONB
);

CREATE INDEX idx_avaliacao_pergunta_questionario_ordem ON avaliacao_pergunta (questionario_id, ordem);

CREATE TABLE ciclo_avaliacao (
    id SERIAL PRIMARY KEY,
    data_criacao TIMESTAMPTZ NOT NULL,
    data_atualizacao TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    questionario_id INTEGER NOT NULL REFERENCES questionario (id),
    nome VARCHAR(150) NOT NULL,
    descricao TEXT,
    data_inicio TIMESTAMPTZ NOT NULL,
    data_fim TIMESTAMPTZ NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL DEFAULT 'aberto'
);

CREATE TABLE avaliacao_docente (
    id SERIAL PRIMARY KEY,
    data_criacao TIMESTAMPTZ NOT NULL,
    data_atualizacao TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    ciclo_id INTEGER NOT NULL REFERENCES ciclo_avaliacao (id),
    aluno_id INTEGER REFERENCES perfil_aluno (id),
    professor_id INTEGER NULL REFERENCES perfil_professor (id),
    turma_id INTEGER NULL REFERENCES turma (id),
    session_key VARCHAR(150),
    hora_inicio TIMESTAMPTZ,
    hora_fim TIMESTAMPTZ,
    CONSTRAINT unique_avaliacao UNIQUE (
        ciclo_id,
        aluno_id,
        professor_id,
        turma_id
    )
);

CREATE TABLE avaliacao_resposta (
    id SERIAL PRIMARY KEY,
    data_criacao TIMESTAMPTZ NOT NULL,
    data_atualizacao TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    avaliacao_id INTEGER NOT NULL REFERENCES avaliacao_docente (id) ON DELETE CASCADE,
    pergunta_id INTEGER NOT NULL REFERENCES avaliacao_pergunta (id),
    aluno_id INTEGER REFERENCES perfil_aluno (id),
    turma_id INTEGER REFERENCES turma (id),
    valor_numerico NUMERIC(10, 2),
    valor_texto TEXT,
    valor_multipla JSONB,
    session_key VARCHAR(150),
    CONSTRAINT unique_resposta UNIQUE (
        avaliacao_id,
        aluno_id,
        pergunta_id,
        session_key
    )
);

CREATE TABLE job_lembrete_ciclo_turma (
    id SERIAL PRIMARY KEY,
    data_criacao TIMESTAMPTZ NOT NULL,
    data_atualizacao TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    ciclo_id INTEGER NOT NULL REFERENCES ciclo_avaliacao (id),
    turma_id INTEGER NOT NULL REFERENCES turma (id),
    status VARCHAR(20) NOT NULL DEFAULT 'pendente',
    proximo_envio_em TIMESTAMPTZ,
    total_alunos_aptos INTEGER NOT NULL DEFAULT 0,
    total_respondentes INTEGER NOT NULL DEFAULT 0,
    taxa_resposta_atual NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    total_emails_enviados INTEGER NOT NULL DEFAULT 0,
    total_falhas INTEGER NOT NULL DEFAULT 0,
    rodadas_executadas INTEGER NOT NULL DEFAULT 0,
    ultima_execucao TIMESTAMPTZ,
    mensagem_erro TEXT,
    UNIQUE (ciclo_id, turma_id)
);

CREATE INDEX idx_job_status_envio ON job_lembrete_ciclo_turma (status, proximo_envio_em);

CREATE INDEX idx_job_ciclo_turma ON job_lembrete_ciclo_turma (ciclo_id, turma_id);

CREATE TABLE notificacao_lembrete (
    id SERIAL PRIMARY KEY,
    data_criacao TIMESTAMPTZ NOT NULL,
    data_atualizacao TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    job_id INTEGER NOT NULL REFERENCES job_lembrete_ciclo_turma (id) ON DELETE CASCADE,
    aluno_id INTEGER NOT NULL REFERENCES perfil_aluno (id),
    status VARCHAR(20) NOT NULL DEFAULT 'pendente',
    rodada INTEGER NOT NULL DEFAULT 1,
    tentativas INTEGER NOT NULL DEFAULT 0,
    enviado_em TIMESTAMPTZ,
    mensagem_id VARCHAR(255),
    motivo_falha TEXT
);

CREATE INDEX idx_notif_job_aluno ON notificacao_lembrete (job_id, aluno_id);

CREATE INDEX idx_notif_status_enviado ON notificacao_lembrete (status, enviado_em);