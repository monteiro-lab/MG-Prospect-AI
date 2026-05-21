import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../services/api';
import { MailX, Loader2, CheckCircle2 } from 'lucide-react';
import logoMendonca from '../assets/logo.png';

export function Unsubscribe() {
    const { token } = useParams();
    
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');

    async function handleUnsubscribe() {
        try {
            await api.post(`/public/unsubscribe/${token}`);
            setStatus('success');
        } catch (error) {
            console.error('Erro ao processar unsubscribe', error);
            setStatus('error');
        }
    }

    useEffect(() => {
        if (token) {
            handleUnsubscribe();
        } else {
            setStatus('error');
        }
    }, [token]);

    return (
        <div className="min-h-screen bg-[#0A0C0E] py-12 px-4 relative flex items-center justify-center">
            {/* Background elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-mg-gold/5 rounded-full blur-[100px]" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-mg-gold/5 rounded-full blur-[100px]" />
            </div>

            <div className="w-full max-w-md bg-mg-surface/80 backdrop-blur-xl border border-mg-border rounded-premium-xl shadow-2xl relative z-10 overflow-hidden p-8 text-center">
                <div className="absolute top-0 left-0 right-0 h-1 bg-gold-gradient" />
                
                <img 
                    src={logoMendonca} 
                    alt="Logo Mendonça Galvão" 
                    className="w-full max-w-[140px] max-h-[70px] object-contain mb-8 mx-auto drop-shadow-md opacity-80" 
                />

                {status === 'loading' && (
                    <div className="flex flex-col items-center justify-center py-8">
                        <Loader2 className="w-10 h-10 text-mg-gold animate-spin mb-4" />
                        <p className="text-mg-muted">Processando sua solicitação...</p>
                    </div>
                )}

                {status === 'success' && (
                    <div className="animate-fade-in">
                        <div className="w-16 h-16 bg-mg-success/10 rounded-full flex items-center justify-center mx-auto mb-6">
                            <CheckCircle2 className="w-8 h-8 text-mg-success" />
                        </div>
                        <h2 className="text-2xl font-bold text-mg-text mb-3">Inscrição Cancelada</h2>
                        <p className="text-mg-muted text-sm leading-relaxed mb-8">
                            Seu e-mail foi removido de nossa lista de contatos com sucesso. 
                            Você não receberá mais comunicações proativas da Mendonça Galvão Contadores Associados.
                        </p>
                    </div>
                )}

                {status === 'error' && (
                    <div className="animate-fade-in">
                        <div className="w-16 h-16 bg-mg-error/10 rounded-full flex items-center justify-center mx-auto mb-6">
                            <MailX className="w-8 h-8 text-mg-error" />
                        </div>
                        <h2 className="text-xl font-bold text-mg-text mb-3">Link Inválido</h2>
                        <p className="text-mg-muted text-sm leading-relaxed mb-8">
                            Este link de cancelamento é inválido ou já expirou. 
                            Se você continuar recebendo e-mails não solicitados, por favor, entre em contato conosco.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
