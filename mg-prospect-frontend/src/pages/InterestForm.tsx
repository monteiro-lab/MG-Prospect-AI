import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Building2, User, Mail, Phone, MapPin, Briefcase, Clock, Send, Loader2, CheckCircle2 } from 'lucide-react';
import logoMendonca from '../assets/logo.png';

export function InterestForm() {
    const { token } = useParams();
    const navigate = useNavigate();
    
    const [loading, setLoading] = useState(token ? true : false);
    const [submitting, setSubmitting] = useState(false);
    const [success, setSuccess] = useState(false);
    
    const [formData, setFormData] = useState({
        company_name: '',
        contact_name: '',
        email: '',
        phone: '',
        city: '',
        segment: '',
        preferred_contact_time: 'Manhã',
        message: '',
        consent: false
    });

    const formatPhone = (value: string) => {
        let v = value.replace(/\D/g, '');
        if (v.length > 11) v = v.slice(0, 11);
        
        if (v.length <= 10) {
            v = v.replace(/^(\d{2})(\d)/g, '($1) $2');
            v = v.replace(/(\d{4})(\d)/, '$1-$2');
        } else {
            v = v.replace(/^(\d{2})(\d)/g, '($1) $2');
            v = v.replace(/(\d{5})(\d)/, '$1-$2');
        }
        return v;
    };

    useEffect(() => {
        if (token) {
            fetchLeadData();
        }
    }, [token]);

    const fetchLeadData = async () => {
        try {
            const response = await api.get(`/public/interest/${token}`);
            setFormData(prev => ({
                ...prev,
                company_name: response.data.company_name || '',
                city: response.data.city || '',
                segment: response.data.segment || ''
            }));
        } catch (error) {
            console.error('Lead token not found or expired', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            await api.post('/public/interest', {
                ...formData,
                lead_token: token || null
            });
            setSuccess(true);
        } catch (error) {
            console.error("Erro ao enviar interesse:", error);
            alert("Ocorreu um erro ao enviar seus dados. Tente novamente.");
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-mg-bg flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-mg-gold animate-spin" />
            </div>
        );
    }

    if (success) {
        return (
            <div className="min-h-screen bg-mg-bg flex items-center justify-center p-4">
                <div className="card-premium max-w-md w-full text-center py-12 relative overflow-hidden">
                    {/* Background glow */}
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-1/2 bg-mg-success/5 blur-3xl pointer-events-none" />
                    
                    <div className="w-16 h-16 bg-mg-success/10 rounded-full flex items-center justify-center mx-auto mb-6 relative z-10 shadow-[0_0_30px_rgba(34,197,94,0.2)]">
                        <CheckCircle2 className="w-8 h-8 text-mg-success" />
                    </div>
                    
                    <h2 className="text-2xl font-bold text-mg-text mb-3 relative z-10">Agradecemos o interesse!</h2>
                    <p className="text-mg-muted mb-8 relative z-10 text-sm leading-relaxed px-4">
                        Recebemos suas informações com sucesso. Nossa equipe especialista já tem seus dados e entrará em contato para entendermos como a Mendonça Galvão pode apoiar o seu negócio.
                    </p>

                    {/* Simulated Log Area */}
                    <div className="bg-[#0B0D10] border border-mg-border/50 rounded-lg p-4 mb-8 text-left text-xs font-mono relative z-10 mx-6 shadow-inner">
                        <div className="flex items-center gap-2 mb-3 border-b border-mg-border/30 pb-2">
                            <div className="w-2 h-2 rounded-full bg-mg-error/70"></div>
                            <div className="w-2 h-2 rounded-full bg-mg-warning/70"></div>
                            <div className="w-2 h-2 rounded-full bg-mg-success/70"></div>
                            <span className="text-mg-muted/50 ml-2 text-[10px] uppercase tracking-wider">Status do Atendimento</span>
                        </div>
                        <div className="space-y-2.5">
                            <div className="flex items-start gap-2 text-mg-success/80 animate-fade-in" style={{ animationDelay: '0ms' }}>
                                <span className="opacity-50 select-none">{'>'}</span>
                                <span>Dados recebidos e validados de forma segura.</span>
                            </div>
                            <div className="flex items-start gap-2 text-mg-success/80 animate-fade-in" style={{ animationDelay: '600ms', animationFillMode: 'both' }}>
                                <span className="opacity-50 select-none">{'>'}</span>
                                <span>Equipe comercial notificada internamente via Slack.</span>
                            </div>
                            <div className="flex items-start gap-2 text-mg-gold animate-fade-in" style={{ animationDelay: '1200ms', animationFillMode: 'both' }}>
                                <span className="opacity-50 select-none">{'>'}</span>
                                <span className="flex items-center gap-2">
                                    Aguardando um consultor entrar em contato...
                                    <Loader2 className="w-3 h-3 animate-spin" />
                                </span>
                            </div>
                        </div>
                    </div>

                    <button onClick={() => navigate('/')} className="btn-secondary relative z-10">
                        Voltar para o Início
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#0A0C0E] py-12 px-4 relative flex items-center justify-center">
            {/* Background elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-mg-gold/5 rounded-full blur-[100px]" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-mg-gold/5 rounded-full blur-[100px]" />
            </div>

            <div className="w-full max-w-2xl bg-mg-surface/80 backdrop-blur-xl border border-mg-border rounded-premium-xl shadow-2xl relative z-10 overflow-hidden">
                {/* Header */}
                <div className="bg-mg-bg/50 border-b border-mg-border p-8 text-center relative">
                    <div className="absolute top-0 left-0 right-0 h-1 bg-gold-gradient" />
                    <img 
                        src={logoMendonca} 
                        alt="Logo Mendonça Galvão" 
                        className="w-full max-w-[160px] max-h-[80px] object-contain mb-4 mx-auto drop-shadow-md" 
                    />
                    <h2 className="mt-2 text-xl font-semibold text-mg-text">Podemos ajudar sua empresa a crescer?</h2>
                    <p className="text-sm text-mg-muted mt-2">
                        Preencha o formulário abaixo e nossa equipe especialista em estruturação contábil B2B entrará em contato.
                    </p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="p-8 space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="label-premium flex items-center gap-1.5"><Building2 className="w-4 h-4 text-mg-gold" /> Nome da Empresa</label>
                            <input type="text" required value={formData.company_name} onChange={e => setFormData({...formData, company_name: e.target.value})} className="input-premium" placeholder="Razão Social ou Fantasia" />
                        </div>
                        <div>
                            <label className="label-premium flex items-center gap-1.5"><User className="w-4 h-4 text-mg-gold" /> Nome do Responsável</label>
                            <input type="text" required value={formData.contact_name} onChange={e => setFormData({...formData, contact_name: e.target.value})} className="input-premium" placeholder="Seu nome" />
                        </div>
                        <div>
                            <label className="label-premium flex items-center gap-1.5"><Mail className="w-4 h-4 text-mg-gold" /> E-mail</label>
                            <input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="input-premium" placeholder="contato@empresa.com" />
                        </div>
                        <div>
                            <label className="label-premium flex items-center gap-1.5"><Phone className="w-4 h-4 text-mg-gold" /> Telefone / WhatsApp</label>
                            <input 
                                type="tel" 
                                required 
                                value={formData.phone} 
                                onChange={e => setFormData({...formData, phone: formatPhone(e.target.value)})} 
                                className="input-premium" 
                                placeholder="(00) 00000-0000"
                                maxLength={15}
                            />
                        </div>
                        <div>
                            <label className="label-premium flex items-center gap-1.5"><MapPin className="w-4 h-4 text-mg-gold" /> Cidade</label>
                            <input type="text" value={formData.city} onChange={e => setFormData({...formData, city: e.target.value})} className="input-premium" placeholder="Ex: Petrolina" />
                        </div>
                        <div>
                            <label className="label-premium flex items-center gap-1.5"><Briefcase className="w-4 h-4 text-mg-gold" /> Segmento</label>
                            <input type="text" value={formData.segment} onChange={e => setFormData({...formData, segment: e.target.value})} className="input-premium" placeholder="Área de atuação" />
                        </div>
                    </div>

                    <div>
                        <label className="label-premium flex items-center gap-1.5"><Clock className="w-4 h-4 text-mg-gold" /> Melhor horário para contato</label>
                        <select value={formData.preferred_contact_time} onChange={e => setFormData({...formData, preferred_contact_time: e.target.value})} className="input-premium">
                            <option value="Manhã">Manhã (08h - 12h)</option>
                            <option value="Tarde">Tarde (14h - 18h)</option>
                            <option value="Qualquer horário">Qualquer horário comercial</option>
                        </select>
                    </div>

                    <div>
                        <label className="label-premium">Mensagem (Opcional)</label>
                        <textarea value={formData.message} onChange={e => setFormData({...formData, message: e.target.value})} rows={3} className="input-premium resize-none" placeholder="Conte-nos brevemente o seu cenário ou dúvida principal..." />
                    </div>

                    <div className="flex items-start gap-3 bg-mg-bg/50 p-4 rounded-premium border border-mg-border">
                        <input type="checkbox" id="consent" required checked={formData.consent} onChange={e => setFormData({...formData, consent: e.target.checked})} className="mt-1 custom-checkbox" />
                        <label htmlFor="consent" className="text-xs text-mg-muted leading-relaxed cursor-pointer">
                            Autorizo a Mendonça Galvão Contadores Associados a entrar em contato comigo pelos canais informados para apresentação de soluções contábeis, ciente de que meus dados serão protegidos conforme a LGPD.
                        </label>
                    </div>

                    <div className="pt-4">
                        <button type="submit" disabled={submitting || !formData.consent} className="w-full btn-primary py-4 text-base font-semibold shadow-glow">
                            {submitting ? (
                                <><Loader2 className="w-5 h-5 animate-spin mr-2" /> Enviando...</>
                            ) : (
                                <><Send className="w-5 h-5 mr-2" /> Solicitar Contato</>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
