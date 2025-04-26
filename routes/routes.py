from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Agendamento
from extensions import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash
from collections import Counter

def init_routes(app):

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def home():
        return render_template('auth/login.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            user = User.query.filter_by(email=request.form['email']).first()
            
            if user and user.senha and user.senha != '' and user.senha != 'null':
                from werkzeug.security import check_password_hash
                if check_password_hash(user.senha, request.form['senha']):
                    login_user(user)
                    return redirect(url_for('admin_dashboard') if user.is_admin else url_for('meus_agendamentos'))
            flash('Credenciais inválidas')
        return render_template('auth/login.html')

    @app.route('/register', methods=['GET', 'POST'])  
    def register():
        if request.method == 'POST':
            hashed_pw = generate_password_hash(request.form['senha'], method='pbkdf2:sha256')
            novo_user = User(
                nome=request.form['nome'],
                email=request.form['email'],
                senha=hashed_pw
            )
            db.session.add(novo_user)
            db.session.commit()
            flash('Cadastro realizado com sucesso!')
            return redirect(url_for('login'))
        return render_template('auth/register.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/agendar', methods=['GET', 'POST'])
    @login_required
    def agendar():
        if request.method == 'POST':
            servico = request.form['servico']
            preco = float(request.form['preco'])
            data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
            hora = datetime.strptime(request.form['hora'], '%H:%M').time()

            # ✅ Verifica se o cliente já tem agendamento para essa data
            agendamento_existente = Agendamento.query.filter_by(cliente_id=current_user.id, data=data).first()
            if agendamento_existente:
                flash('Você já possui um agendamento para esta data. Apenas um agendamento por dia é permitido.')
                return redirect(url_for('agendar'))

            # ✅ Verifica se o horário já está ocupado por outro cliente
            conflito = Agendamento.query.filter_by(data=data, hora=hora).first()
            if conflito:
                flash('Este horário já está ocupado. Escolha outro.')
                return redirect(url_for('agendar'))

            novo = Agendamento(
                cliente_id=current_user.id,
                servico=servico,
                preco=preco,
                data=data,
                hora=hora
            )
            db.session.add(novo)
            db.session.commit()
            flash('Agendamento realizado com sucesso.')
            return redirect(url_for('meus_agendamentos'))

        return render_template('pages/agendar.html')


    @app.route('/horarios-disponiveis', methods=['POST'])
    @login_required
    def horarios_disponiveis():
        from datetime import time, timedelta, datetime

        data = request.form.get('data')
        if not data:
            return jsonify([])

        data_obj = datetime.strptime(data, '%Y-%m-%d').date()

        # Definir intervalo de funcionamento: 09:00 às 18:00
        inicio = datetime.combine(data_obj, time(9, 0))
        fim = datetime.combine(data_obj, time(18, 0))
        intervalo = timedelta(minutes=30)

        horarios_possiveis = []
        atual = inicio
        while atual <= fim:
            horarios_possiveis.append(atual.time().strftime('%H:%M'))
            atual += intervalo

        # Buscar horários já ocupados
        agendados = Agendamento.query.filter_by(data=data_obj).with_entities(Agendamento.hora).all()
        ocupados = {hora.strftime('%H:%M') for (hora,) in agendados}

        livres = [h for h in horarios_possiveis if h not in ocupados]
        return jsonify(livres)



    @app.route('/meus-agendamentos')
    @login_required
    def meus_agendamentos():
        agendamentos = Agendamento.query.filter_by(cliente_id=current_user.id).order_by(Agendamento.data.desc()).all()
        return render_template('pages/meus_agendamentos.html', agendamentos=agendamentos)

    @app.route('/admin-dashboard')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            return redirect(url_for('home'))

        agendamentos = Agendamento.query.all()
        lucro_total = sum(a.preco for a in agendamentos)

        # Lucro por mês
        ag_por_mes = {}
        for a in agendamentos:
            chave = a.data.strftime('%Y-%m')
            ag_por_mes[chave] = ag_por_mes.get(chave, 0) + a.preco

        # Serviço mais popular e distribuição de serviços
        servicos = Counter(a.servico for a in agendamentos)

        # Total no mês atual
        from datetime import date
        hoje = date.today()
        agendamentos_mes = sum(1 for a in agendamentos if a.data.month == hoje.month and a.data.year == hoje.year)

        # Dia mais movimentado
        dias = Counter(a.data.strftime('%A') for a in agendamentos)
        dia_mais_movimentado = dias.most_common(1)[0][0] if dias else 'Indefinido'

        # Serviço mais vendido
        servico_popular = servicos.most_common(1)[0][0] if servicos else 'Indefinido'

        # Calendário
        agendamentos_json = [
            {
                "title": f"{a.servico} - R$ {a.preco:.2f}<br>Cliente: {a.cliente.nome}",
                "start": a.data.strftime('%Y-%m-%d'),
                "allDay": True
            } for a in agendamentos
        ]


        return render_template(
            'dashboard/admin_dashboard.html',
            lucro_total=lucro_total,
            ag_por_mes=ag_por_mes,
            servicos=servicos,
            agendamentos_mes=agendamentos_mes,
            servico_popular=servico_popular,
            dia_mais_movimentado=dia_mais_movimentado,
            agendamentos_json=agendamentos_json
        )
        

    @app.route('/admin/cancelar-agendamento', methods=['POST'])
    @login_required
    def admin_cancelar_agendamento():
        if not current_user.is_admin:
            return redirect(url_for('home'))

        agendamento_id = request.form.get('agendamento_id')
        agendamento = Agendamento.query.get(agendamento_id)

        if agendamento:
            db.session.delete(agendamento)
            db.session.commit()
            flash("Agendamento cancelado com sucesso.", "success")
        else:
            flash("Agendamento não encontrado.", "danger")

        return redirect(url_for('gerenciar_agendamentos'))


    @app.route('/admin/agendamentos')
    @login_required
    def gerenciar_agendamentos():
        if not current_user.is_admin:
            return redirect(url_for('home'))

        from datetime import date
        agendamentos = Agendamento.query.filter(Agendamento.data >= date.today()).order_by(Agendamento.data).all()
        return render_template('dashboard/gerenciar_agendamentos.html', agendamentos=agendamentos)

    @app.route('/cancelar-agendamento', methods=['POST'])
    @login_required
    def cancelar_agendamento():
        agendamento_id = request.form.get('agendamento_id')
        agendamento = Agendamento.query.filter_by(id=agendamento_id, cliente_id=current_user.id).first()

        if agendamento:
            db.session.delete(agendamento)
            db.session.commit()
            flash('Agendamento cancelado com sucesso.')
        else:
            flash('Agendamento não encontrado ou não pertence a você.')

        return redirect(url_for('meus_agendamentos'))
