-- ============================================================================
-- SCHEMA SQL - Sistema de Avaliação Docente
-- ============================================================================
-- Gerado a partir dos modelos Django
-- Data: 17 de novembro de 2025
-- Repositório: AeVALIS.SGAD
-- Branch: Homologacao
-- ============================================================================

-- ============================================================================
-- TABELAS DE PERFIL DE USUÁRIOS
-- ============================================================================

-- Perfil de Aluno
CREATE TABLE IF NOT EXISTS avaliacao_docente_perfilaluno (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    situacao VARCHAR(45) DEFAULT 'Ativo' NOT NULL,
    CONSTRAINT fk_perfilaluno_user FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE CASCADE
);

CREATE INDEX idx_perfilaluno_user_id ON avaliacao_docente_perfilaluno (user_id);

-- Perfil de Professor
CREATE TABLE IF NOT EXISTS avaliacao_docente_perfilprofessor (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    registro_academico VARCHAR(45) NOT NULL,
    CONSTRAINT fk_perfilprofessor_user FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE CASCADE
);

CREATE INDEX idx_perfilprofessor_user_id ON avaliacao_docente_perfilprofessor (user_id);

-- ============================================================================
-- TABELAS DE ESTRUTURA ACADÊMICA
-- ============================================================================

-- Período Letivo
CREATE TABLE IF NOT EXISTS avaliacao_docente_periodoletivo (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    ano INTEGER NOT NULL,
    semestre INTEGER NOT NULL CHECK (semestre BETWEEN 1 AND 10),
    CONSTRAINT unique_periodo UNIQUE (ano, semestre)
);

CREATE INDEX idx_periodoletivo_ano_semestre ON avaliacao_docente_periodoletivo (ano, semestre);

-- Curso
CREATE TABLE IF NOT EXISTS avaliacao_docente_curso (
    id SERIAL PRIMARY KEY,
    curso_nome VARCHAR(45) NOT NULL,
    curso_sigla VARCHAR(10) NOT NULL,
    coordenador_curso_id INTEGER NOT NULL,
    ativo BOOLEAN DEFAULT TRUE NOT NULL,
    data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_exclusao TIMESTAMP
    WITH
        TIME ZONE NULL,
        CONSTRAINT fk_curso_coordenador FOREIGN KEY (coordenador_curso_id) REFERENCES avaliacao_docente_perfilprofessor (id) ON DELETE CASCADE
);

CREATE INDEX idx_curso_ativo ON avaliacao_docente_curso (ativo);

CREATE INDEX idx_curso_coordenador ON avaliacao_docente_curso (coordenador_curso_id);

-- Disciplina
CREATE TABLE IF NOT EXISTS avaliacao_docente_disciplina (
    id SERIAL PRIMARY KEY,
    disciplina_nome VARCHAR(100) NOT NULL,
    disciplina_sigla VARCHAR(45) NOT NULL,
    disciplina_tipo VARCHAR(45) NOT NULL CHECK (
        disciplina_tipo IN ('Obrigatória', 'Optativa')
    ),
    curso_id INTEGER NOT NULL,
    professor_id INTEGER NOT NULL,
    periodo_letivo_id INTEGER NOT NULL,
    ativo BOOLEAN DEFAULT TRUE NOT NULL,
    data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_exclusao TIMESTAMP
    WITH
        TIME ZONE NULL,
        CONSTRAINT fk_disciplina_curso FOREIGN KEY (curso_id) REFERENCES avaliacao_docente_curso (id) ON DELETE CASCADE,
        CONSTRAINT fk_disciplina_professor FOREIGN KEY (professor_id) REFERENCES avaliacao_docente_perfilprofessor (id) ON DELETE CASCADE,
        CONSTRAINT fk_disciplina_periodo FOREIGN KEY (periodo_letivo_id) REFERENCES avaliacao_docente_periodoletivo (id) ON DELETE CASCADE
);

CREATE INDEX idx_disciplina_ativo ON avaliacao_docente_disciplina (ativo);

CREATE INDEX idx_disciplina_curso ON avaliacao_docente_disciplina (curso_id);

CREATE INDEX idx_disciplina_professor ON avaliacao_docente_disciplina (professor_id);

CREATE INDEX idx_disciplina_periodo ON avaliacao_docente_disciplina (periodo_letivo_id);

-- Turma
CREATE TABLE IF NOT EXISTS avaliacao_docente_turma (
    id SERIAL PRIMARY KEY,
    codigo_turma VARCHAR(100) UNIQUE NOT NULL,
    disciplina_id INTEGER NOT NULL,
    turno VARCHAR(15) NOT NULL CHECK (
        turno IN (
            'matutino',
            'vespertino',
            'noturno'
        )
    ),
    status VARCHAR(15) DEFAULT 'ativa' NOT NULL CHECK (
        status IN ('ativa', 'finalizada')
    ),
    ativo BOOLEAN DEFAULT TRUE NOT NULL,
    data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_exclusao TIMESTAMP
    WITH
        TIME ZONE NULL,
        CONSTRAINT fk_turma_disciplina FOREIGN KEY (disciplina_id) REFERENCES avaliacao_docente_disciplina (id) ON DELETE CASCADE,
        CONSTRAINT unique_turma_disciplina_turno UNIQUE (disciplina_id, turno)
);

CREATE INDEX idx_turma_ativo ON avaliacao_docente_turma (ativo);

CREATE INDEX idx_turma_disciplina ON avaliacao_docente_turma (disciplina_id);

CREATE INDEX idx_turma_status ON avaliacao_docente_turma (status);

-- Matrícula em Turma
CREATE TABLE IF NOT EXISTS avaliacao_docente_matriculaturma (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER NOT NULL,
    turma_id INTEGER NOT NULL,
    data_matricula TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        status VARCHAR(15) DEFAULT 'ativa' NOT NULL CHECK (
            status IN (
                'ativa',
                'trancada',
                'cancelada',
                'concluida'
            )
        ),
        ativo BOOLEAN DEFAULT TRUE NOT NULL,
        data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_exclusao TIMESTAMP
    WITH
        TIME ZONE NULL,
        CONSTRAINT fk_matricula_aluno FOREIGN KEY (aluno_id) REFERENCES avaliacao_docente_perfilaluno (id) ON DELETE CASCADE,
        CONSTRAINT fk_matricula_turma FOREIGN KEY (turma_id) REFERENCES avaliacao_docente_turma (id) ON DELETE CASCADE,
        CONSTRAINT unique_matricula_aluno_turma UNIQUE (aluno_id, turma_id)
);

CREATE INDEX idx_matricula_ativo ON avaliacao_docente_matriculaturma (ativo);

CREATE INDEX idx_matricula_aluno ON avaliacao_docente_matriculaturma (aluno_id);

CREATE INDEX idx_matricula_turma ON avaliacao_docente_matriculaturma (turma_id);

CREATE INDEX idx_matricula_status ON avaliacao_docente_matriculaturma (status);

-- Horário de Turma
CREATE TABLE IF NOT EXISTS avaliacao_docente_horarioturma (
    id SERIAL PRIMARY KEY,
    turma_id INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 1 AND 6),
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,
    CONSTRAINT fk_horario_turma FOREIGN KEY (turma_id) REFERENCES avaliacao_docente_turma (id) ON DELETE CASCADE,
    CONSTRAINT unique_horario_turma UNIQUE (
        turma_id,
        dia_semana,
        hora_inicio
    )
);

CREATE INDEX idx_horario_turma ON avaliacao_docente_horarioturma (turma_id);

CREATE INDEX idx_horario_dia ON avaliacao_docente_horarioturma (dia_semana);

-- ============================================================================
-- TABELAS DE AVALIAÇÃO DOCENTE
-- ============================================================================

-- Questionário de Avaliação
CREATE TABLE IF NOT EXISTS avaliacao_docente_questionarioavaliacao (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    descricao TEXT,
    criado_por_id INTEGER NOT NULL,
    ativo BOOLEAN DEFAULT TRUE NOT NULL,
    data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_exclusao TIMESTAMP
    WITH
        TIME ZONE NULL,
        CONSTRAINT fk_questionario_criador FOREIGN KEY (criado_por_id) REFERENCES auth_user (id) ON DELETE CASCADE
);

CREATE INDEX idx_questionario_ativo ON avaliacao_docente_questionarioavaliacao (ativo);

CREATE INDEX idx_questionario_criador ON avaliacao_docente_questionarioavaliacao (criado_por_id);

-- Categoria de Pergunta
CREATE TABLE IF NOT EXISTS avaliacao_docente_categoriapergunta (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) UNIQUE NOT NULL,
    descricao TEXT,
    ordem INTEGER DEFAULT 0 NOT NULL,
    ativo BOOLEAN DEFAULT TRUE NOT NULL,
    data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_exclusao TIMESTAMP
    WITH
        TIME ZONE NULL
);

CREATE INDEX idx_categoria_ativo ON avaliacao_docente_categoriapergunta (ativo);

CREATE INDEX idx_categoria_ordem ON avaliacao_docente_categoriapergunta (ordem);

-- Pergunta de Avaliação
CREATE TABLE IF NOT EXISTS avaliacao_docente_perguntaavaliacao (
    id SERIAL PRIMARY KEY,
    enunciado TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (
        tipo IN (
            'likert',
            'nps',
            'multipla_escolha',
            'sim_nao',
            'texto_livre'
        )
    ),
    categoria_id INTEGER NOT NULL,
    obrigatoria BOOLEAN DEFAULT TRUE NOT NULL,
    opcoes_multipla_escolha JSONB NULL,
    ativo BOOLEAN DEFAULT TRUE NOT NULL,
    data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_exclusao TIMESTAMP
    WITH
        TIME ZONE NULL,
        CONSTRAINT fk_pergunta_categoria FOREIGN KEY (categoria_id) REFERENCES avaliacao_docente_categoriapergunta (id) ON DELETE CASCADE
);

CREATE INDEX idx_pergunta_ativo ON avaliacao_docente_perguntaavaliacao (ativo);

CREATE INDEX idx_pergunta_categoria ON avaliacao_docente_perguntaavaliacao (categoria_id);

CREATE INDEX idx_pergunta_tipo ON avaliacao_docente_perguntaavaliacao (tipo);

-- Relacionamento Questionário-Pergunta
CREATE TABLE IF NOT EXISTS avaliacao_docente_questionariopergunta (
    id SERIAL PRIMARY KEY,
    questionario_id INTEGER NOT NULL,
    pergunta_id INTEGER NOT NULL,
    ordem_no_questionario INTEGER DEFAULT 0 NOT NULL,
    ativo BOOLEAN DEFAULT TRUE NOT NULL,
    data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_exclusao TIMESTAMP
    WITH
        TIME ZONE NULL,
        CONSTRAINT fk_qp_questionario FOREIGN KEY (questionario_id) REFERENCES avaliacao_docente_questionarioavaliacao (id) ON DELETE CASCADE,
        CONSTRAINT fk_qp_pergunta FOREIGN KEY (pergunta_id) REFERENCES avaliacao_docente_perguntaavaliacao (id) ON DELETE CASCADE,
        CONSTRAINT unique_questionario_pergunta UNIQUE (questionario_id, pergunta_id)
);

CREATE INDEX idx_qp_ativo ON avaliacao_docente_questionariopergunta (ativo);

CREATE INDEX idx_qp_questionario ON avaliacao_docente_questionariopergunta (questionario_id);

CREATE INDEX idx_qp_pergunta ON avaliacao_docente_questionariopergunta (pergunta_id);

CREATE INDEX idx_qp_ordem ON avaliacao_docente_questionariopergunta (ordem_no_questionario);

-- Ciclo de Avaliação
CREATE TABLE IF NOT EXISTS avaliacao_docente_cicloavaliacao (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    periodo_letivo_id INTEGER NOT NULL,
    data_inicio TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_fim TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        questionario_id INTEGER NOT NULL,
        permite_avaliacao_anonima BOOLEAN DEFAULT TRUE NOT NULL,
        permite_multiplas_respostas BOOLEAN DEFAULT FALSE NOT NULL,
        enviar_lembrete_email BOOLEAN DEFAULT TRUE NOT NULL,
        encerrado BOOLEAN DEFAULT FALSE NOT NULL,
        data_encerramento TIMESTAMP
    WITH
        TIME ZONE NULL,
        criado_por_id INTEGER NOT NULL,
        ativo BOOLEAN DEFAULT TRUE NOT NULL,
        data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_exclusao TIMESTAMP
    WITH
        TIME ZONE NULL,
        CONSTRAINT fk_ciclo_periodo FOREIGN KEY (periodo_letivo_id) REFERENCES avaliacao_docente_periodoletivo (id) ON DELETE CASCADE,
        CONSTRAINT fk_ciclo_questionario FOREIGN KEY (questionario_id) REFERENCES avaliacao_docente_questionarioavaliacao (id) ON DELETE CASCADE,
        CONSTRAINT fk_ciclo_criador FOREIGN KEY (criado_por_id) REFERENCES auth_user (id) ON DELETE CASCADE
);

CREATE INDEX idx_ciclo_ativo ON avaliacao_docente_cicloavaliacao (ativo);

CREATE INDEX idx_ciclo_periodo ON avaliacao_docente_cicloavaliacao (periodo_letivo_id);

CREATE INDEX idx_ciclo_questionario ON avaliacao_docente_cicloavaliacao (questionario_id);

CREATE INDEX idx_ciclo_encerrado ON avaliacao_docente_cicloavaliacao (encerrado);

CREATE INDEX idx_ciclo_datas ON avaliacao_docente_cicloavaliacao (data_inicio, data_fim);

-- Tabela de relacionamento ManyToMany: Ciclo <-> Turmas
CREATE TABLE IF NOT EXISTS avaliacao_docente_cicloavaliacao_turmas (
    id SERIAL PRIMARY KEY,
    cicloavaliacao_id INTEGER NOT NULL,
    turma_id INTEGER NOT NULL,
    CONSTRAINT fk_ciclo_turmas_ciclo FOREIGN KEY (cicloavaliacao_id) REFERENCES avaliacao_docente_cicloavaliacao (id) ON DELETE CASCADE,
    CONSTRAINT fk_ciclo_turmas_turma FOREIGN KEY (turma_id) REFERENCES avaliacao_docente_turma (id) ON DELETE CASCADE,
    CONSTRAINT unique_ciclo_turma UNIQUE (cicloavaliacao_id, turma_id)
);

CREATE INDEX idx_ciclo_turmas_ciclo ON avaliacao_docente_cicloavaliacao_turmas (cicloavaliacao_id);

CREATE INDEX idx_ciclo_turmas_turma ON avaliacao_docente_cicloavaliacao_turmas (turma_id);

-- Avaliação Docente
CREATE TABLE IF NOT EXISTS avaliacao_docente_avaliacaodocente (
    id SERIAL PRIMARY KEY,
    ciclo_id INTEGER NOT NULL,
    turma_id INTEGER NOT NULL,
    professor_id INTEGER NOT NULL,
    disciplina_id INTEGER NOT NULL,
    status VARCHAR(15) DEFAULT 'pendente' NOT NULL CHECK (
        status IN (
            'pendente',
            'em_andamento',
            'finalizada',
            'cancelada'
        )
    ),
    ativo BOOLEAN DEFAULT TRUE NOT NULL,
    data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_exclusao TIMESTAMP
    WITH
        TIME ZONE NULL,
        CONSTRAINT fk_avaliacao_ciclo FOREIGN KEY (ciclo_id) REFERENCES avaliacao_docente_cicloavaliacao (id) ON DELETE CASCADE,
        CONSTRAINT fk_avaliacao_turma FOREIGN KEY (turma_id) REFERENCES avaliacao_docente_turma (id) ON DELETE CASCADE,
        CONSTRAINT fk_avaliacao_professor FOREIGN KEY (professor_id) REFERENCES avaliacao_docente_perfilprofessor (id) ON DELETE CASCADE,
        CONSTRAINT fk_avaliacao_disciplina FOREIGN KEY (disciplina_id) REFERENCES avaliacao_docente_disciplina (id) ON DELETE CASCADE,
        CONSTRAINT unique_avaliacao UNIQUE (
            ciclo_id,
            turma_id,
            professor_id,
            disciplina_id
        )
);

CREATE INDEX idx_avaliacao_ativo ON avaliacao_docente_avaliacaodocente (ativo);

CREATE INDEX idx_avaliacao_ciclo ON avaliacao_docente_avaliacaodocente (ciclo_id);

CREATE INDEX idx_avaliacao_turma ON avaliacao_docente_avaliacaodocente (turma_id);

CREATE INDEX idx_avaliacao_professor ON avaliacao_docente_avaliacaodocente (professor_id);

CREATE INDEX idx_avaliacao_disciplina ON avaliacao_docente_avaliacaodocente (disciplina_id);

CREATE INDEX idx_avaliacao_status ON avaliacao_docente_avaliacaodocente (status);

-- Resposta de Avaliação
CREATE TABLE IF NOT EXISTS avaliacao_docente_respostaavaliacao (
    id SERIAL PRIMARY KEY,
    avaliacao_id INTEGER NOT NULL,
    aluno_id INTEGER NULL,
    pergunta_id INTEGER NOT NULL,
    valor_texto TEXT,
    valor_numerico INTEGER NULL,
    valor_boolean BOOLEAN NULL,
    data_resposta TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        anonima BOOLEAN DEFAULT FALSE NOT NULL,
        session_key VARCHAR(40),
        ativo BOOLEAN DEFAULT TRUE NOT NULL,
        data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_exclusao TIMESTAMP
    WITH
        TIME ZONE NULL,
        CONSTRAINT fk_resposta_avaliacao FOREIGN KEY (avaliacao_id) REFERENCES avaliacao_docente_avaliacaodocente (id) ON DELETE CASCADE,
        CONSTRAINT fk_resposta_aluno FOREIGN KEY (aluno_id) REFERENCES avaliacao_docente_perfilaluno (id) ON DELETE CASCADE,
        CONSTRAINT fk_resposta_pergunta FOREIGN KEY (pergunta_id) REFERENCES avaliacao_docente_perguntaavaliacao (id) ON DELETE CASCADE,
        CONSTRAINT unique_resposta UNIQUE (
            avaliacao_id,
            aluno_id,
            pergunta_id,
            session_key
        )
);

CREATE INDEX idx_resposta_ativo ON avaliacao_docente_respostaavaliacao (ativo);

CREATE INDEX idx_resposta_avaliacao ON avaliacao_docente_respostaavaliacao (avaliacao_id);

CREATE INDEX idx_resposta_aluno ON avaliacao_docente_respostaavaliacao (aluno_id);

CREATE INDEX idx_resposta_pergunta ON avaliacao_docente_respostaavaliacao (pergunta_id);

CREATE INDEX idx_resposta_anonima ON avaliacao_docente_respostaavaliacao (anonima);

-- ============================================================================
-- TABELAS DE LEMBRETES
-- ============================================================================

-- Job de Lembrete por Ciclo/Turma
CREATE TABLE IF NOT EXISTS avaliacao_docente_joblembreteciclturma (
    id SERIAL PRIMARY KEY,
    ciclo_id INTEGER NOT NULL,
    turma_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pendente' NOT NULL CHECK (
        status IN (
            'pendente',
            'em_execucao',
            'completo',
            'pausado',
            'erro'
        )
    ),
    proximo_envio_em TIMESTAMP
    WITH
        TIME ZONE NULL,
        total_alunos_aptos INTEGER DEFAULT 0 NOT NULL,
        total_respondentes INTEGER DEFAULT 0 NOT NULL,
        taxa_resposta_atual DECIMAL(5, 2) DEFAULT 0.00 NOT NULL,
        total_emails_enviados INTEGER DEFAULT 0 NOT NULL,
        total_falhas INTEGER DEFAULT 0 NOT NULL,
        rodadas_executadas INTEGER DEFAULT 0 NOT NULL,
        ultima_execucao TIMESTAMP
    WITH
        TIME ZONE NULL,
        mensagem_erro TEXT,
        data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        CONSTRAINT fk_job_ciclo FOREIGN KEY (ciclo_id) REFERENCES avaliacao_docente_cicloavaliacao (id) ON DELETE CASCADE,
        CONSTRAINT fk_job_turma FOREIGN KEY (turma_id) REFERENCES avaliacao_docente_turma (id) ON DELETE CASCADE,
        CONSTRAINT unique_job_ciclo_turma UNIQUE (ciclo_id, turma_id)
);

CREATE INDEX idx_job_status_proximo ON avaliacao_docente_joblembreteciclturma (status, proximo_envio_em);

CREATE INDEX idx_job_ciclo_turma ON avaliacao_docente_joblembreteciclturma (ciclo_id, turma_id);

-- Notificação de Lembrete
CREATE TABLE IF NOT EXISTS avaliacao_docente_notificacaolembrete (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL,
    aluno_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pendente' NOT NULL CHECK (
        status IN (
            'pendente',
            'enviado',
            'falhou',
            'ignorado'
        )
    ),
    rodada INTEGER DEFAULT 1 NOT NULL,
    tentativas INTEGER DEFAULT 0 NOT NULL,
    enviado_em TIMESTAMP
    WITH
        TIME ZONE NULL,
        mensagem_id VARCHAR(255),
        motivo_falha TEXT,
        data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        CONSTRAINT fk_notif_job FOREIGN KEY (job_id) REFERENCES avaliacao_docente_joblembreteciclturma (id) ON DELETE CASCADE,
        CONSTRAINT fk_notif_aluno FOREIGN KEY (aluno_id) REFERENCES avaliacao_docente_perfilaluno (id) ON DELETE CASCADE
);

CREATE INDEX idx_notif_job_aluno ON avaliacao_docente_notificacaolembrete (job_id, aluno_id);

CREATE INDEX idx_notif_status_enviado ON avaliacao_docente_notificacaolembrete (status, enviado_em);

-- Lembrete de Avaliação (controle de duplicação)
CREATE TABLE IF NOT EXISTS avaliacao_docente_lembrete_avaliacao (
    id SERIAL PRIMARY KEY,
    ciclo_id INTEGER NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (
        tipo IN ('criacao', 'dois_dias')
    ),
    data_envio TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        total_enviados INTEGER DEFAULT 0 NOT NULL,
        data_criacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        data_atualizacao TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        CONSTRAINT fk_lembrete_ciclo FOREIGN KEY (ciclo_id) REFERENCES avaliacao_docente_cicloavaliacao (id) ON DELETE CASCADE,
        CONSTRAINT unique_lembrete_ciclo_tipo UNIQUE (ciclo_id, tipo)
);

CREATE INDEX idx_lembrete_ciclo_tipo ON avaliacao_docente_lembrete_avaliacao (ciclo_id, tipo);

CREATE INDEX idx_lembrete_data_envio ON avaliacao_docente_lembrete_avaliacao (data_envio);

-- ============================================================================
-- TABELA DE CONFIGURAÇÃO DO SITE
-- ============================================================================

-- Configuração do Site (Singleton)
CREATE TABLE IF NOT EXISTS avaliacao_docente_configuracaosite (
    id SERIAL PRIMARY KEY CHECK (id = 1), -- Garante singleton
    metodo_envio_email VARCHAR(10) DEFAULT 'api' NOT NULL CHECK (
        metodo_envio_email IN ('api', 'smtp')
    ),
    email_notificacao_erros VARCHAR(255) NULL,
    limiar_minimo_percentual DECIMAL(5, 2) DEFAULT 10.00 NOT NULL,
    frequencia_lembrete_horas INTEGER DEFAULT 48 NOT NULL,
    max_lembretes_por_aluno INTEGER DEFAULT 3 NOT NULL
);

-- ============================================================================
-- COMENTÁRIOS E DOCUMENTAÇÃO
-- ============================================================================

COMMENT ON
TABLE avaliacao_docente_perfilaluno IS 'Perfil estendido para usuários do tipo Aluno';

COMMENT ON
TABLE avaliacao_docente_perfilprofessor IS 'Perfil estendido para usuários do tipo Professor';

COMMENT ON
TABLE avaliacao_docente_periodoletivo IS 'Períodos letivos (semestres)';

COMMENT ON
TABLE avaliacao_docente_curso IS 'Cursos oferecidos pela instituição';

COMMENT ON
TABLE avaliacao_docente_disciplina IS 'Disciplinas vinculadas a cursos e períodos';

COMMENT ON
TABLE avaliacao_docente_turma IS 'Turmas de disciplinas com horários específicos';

COMMENT ON
TABLE avaliacao_docente_matriculaturma IS 'Matrículas de alunos em turmas';

COMMENT ON
TABLE avaliacao_docente_horarioturma IS 'Horários de aulas das turmas';

COMMENT ON
TABLE avaliacao_docente_questionarioavaliacao IS 'Templates de questionários reutilizáveis';

COMMENT ON
TABLE avaliacao_docente_categoriapergunta IS 'Categorias para organizar perguntas (ex: Didática, Relacionamento)';

COMMENT ON
TABLE avaliacao_docente_perguntaavaliacao IS 'Perguntas que compõem os questionários';

COMMENT ON
TABLE avaliacao_docente_questionariopergunta IS 'Relacionamento M2M entre questionários e perguntas';

COMMENT ON
TABLE avaliacao_docente_cicloavaliacao IS 'Ciclos/períodos de avaliação institucional';

COMMENT ON
TABLE avaliacao_docente_avaliacaodocente IS 'Avaliações específicas de professores por turma';

COMMENT ON
TABLE avaliacao_docente_respostaavaliacao IS 'Respostas dos alunos às perguntas das avaliações';

COMMENT ON
TABLE avaliacao_docente_joblembreteciclturma IS 'Jobs de envio automático de lembretes por turma';

COMMENT ON
TABLE avaliacao_docente_notificacaolembrete IS 'Registro de notificações individuais enviadas';

COMMENT ON
TABLE avaliacao_docente_lembrete_avaliacao IS 'Controle de envio de lembretes para evitar duplicação';

COMMENT ON
TABLE avaliacao_docente_configuracaosite IS 'Configurações globais do sistema (singleton)';

-- ============================================================================
-- COMENTÁRIOS EM CAMPOS IMPORTANTES
-- ============================================================================

COMMENT ON COLUMN avaliacao_docente_turma.codigo_turma IS 'Código único da turma (ex: INFO3A-2024.1)';

COMMENT ON COLUMN avaliacao_docente_cicloavaliacao.encerrado IS 'Indica se o ciclo foi encerrado manualmente';

COMMENT ON COLUMN avaliacao_docente_respostaavaliacao.anonima IS 'Indica se a resposta é anônima';

COMMENT ON COLUMN avaliacao_docente_respostaavaliacao.session_key IS 'Chave de sessão para respostas anônimas';

COMMENT ON COLUMN avaliacao_docente_joblembreteciclturma.taxa_resposta_atual IS 'Percentual de alunos que já responderam';

COMMENT ON COLUMN avaliacao_docente_configuracaosite.limiar_minimo_percentual IS 'Percentual mínimo de respostas por turma para parar lembretes';

-- ============================================================================
-- FIM DO SCHEMA
-- ============================================================================