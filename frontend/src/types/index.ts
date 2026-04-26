// Types for the Mercado Público system

export interface User {
  id: number;
  nome: string;
  email: string;
  role: 'admin' | 'operator' | 'viewer';
  status: 'pending' | 'active' | 'inactive';
  fiscal_id: number | null;
  created_at: string;
}

export interface Fiscal {
  id: number;
  nome: string;
  matricula: string | null;
  telefone: string | null;
  email: string | null;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface Cessionario {
  id: number;
  nome: string;
  numero_box: string | null;
  atividade: string | null;
  telefone: string | null;
  situacao: 'Regular' | 'Irregular';
  valor_referencia: number;
  periodicidade_referencia: 'Mensal' | 'Semanal' | 'Quinzenal' | 'Único';
  observacoes: string | null;
  fiscal_id: number | null;
  fiscal_nome?: string | null;
  created_at: string;
  updated_at: string;
  ultimo_pagamento?: string;
}

export interface Pagamento {
  id: number;
  cessionario_id: number;
  cessionario_nome?: string;
  cessionario_telefone?: string | null;
  valor: number;
  data_pagamento: string;
  periodicidade: 'Mensal' | 'Semanal' | 'Quinzenal' | 'Único';
  referencia_mes: string | null;
  observacoes: string | null;
  registrado_por_nome?: string;
  created_at: string;
}

export interface DashboardKPIs {
  total_cessionarios: number;
  total_regulares: number;
  total_irregulares: number;
  total_pagamentos_mes: number;
  total_pagamentos_semana: number;
}

export interface ChartData {
  labels: string[];
  values: number[];
}

export interface DashboardData {
  kpis: DashboardKPIs;
  arrecadacao_mensal: ChartData;
  situacao_chart: ChartData;
  top_cessionarios: Array<{
    nome: string;
    box: string;
    total: number;
  }>;
  atividades_recentes: Array<{
    tipo: string;
    cessionario: string;
    valor: number;
    data: string;
  }>;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
}

export type RelatorioTipo = 
  | 'todos' 
  | 'regulares' 
  | 'irregulares' 
  | 'pagamentos' 
  | 'cobranca' 
  | 'cessionarios';

export type ExportFormato = 'pdf' | 'excel';

export interface RelatorioFiltros {
  tipo: RelatorioTipo;
  data_inicio?: string;
  data_fim?: string;
  data_referencia?: string;
  data_cobranca?: string;
  fiscal_id?: number;
  formato: ExportFormato;
}
