#!/bin/env python3

### Notas


# Pretty print para imprimir valores de teste
import pprint
ppp = pprint.PrettyPrinter( indent=4, width=102 )
pp = ppp.pprint

import unittest
from typing import List, Dict, Tuple





class Grade:
    """Representação de nota.
Usa o valor da nota brasileira como representação interna porque a faixa de valores é mais geral que
a estado-unidense."""

    
    us_br_map = { # para conversão
        'a': (90, 100), #intervalos fechados
        'b': (70,  89),
        'c': (50,  69),
        'd': (30,  49),
        'f': (0,   29),
    }


    def __init__( self, br_grade : int = 0 ):
        if not 0 <= br_grade <= 100:
            raise RuntimeError( 'Nota fora do valor aceitável [0, 100]: %.1f' % br_grade )
        self.br_grade = br_grade


    def __repr__( self ):
        return f"Grade( {self.br_grade} )"


    @property
    def us_grade( self ):
        """Nota americana."""
        for us, br_inter in Grade.us_br_map.items():
            if br_inter[0] <= self.br_grade <= br_inter[1]:
                return us


    @us_grade.setter
    def us_grade( self, us_grade : str ):
        us_grade = us_grade.casefold() # só compara em minúsculas
        us_v = Grade.us_br_map.get( us_grade )
        if not us_v:
            raise RuntimeError( 'Nota fora do valor aceitável [abcdf]: %s' % us_grade )
 
        self.br_grade = us_v[0]



    def avg( self, prova2 ):
        """Média entre as duas provas"""
        return Grade( ( self.br_grade + prova2.br_grade ) // 2 )
    
        
def GradeUs( us_grade : str ) -> Grade:
    """Cria nota a partir da nota americana."""
    g = Grade()
    g.us_grade = us_grade
    return g





class ClassGrades:

    MEDIA_APROV = 50

    
    def __init__( self, nome : str,
                  prova1 : Grade = None,
                  prova2 : Grade = None,
                  avg : Grade = None,
                  credit=0 ):
        self.nome = nome
        self.prova1 = prova1
        self.prova2 = prova2
        self._avg = avg
        self.credit = credit


    @property
    def avg( self ) -> Grade:
        #Atualiza se ambas as notas estiverem definidas
        if self.prova1 is None or self.prova2 is None:
            return self._avg
        self._avg = self.prova1.avg( self.prova2 )
        return self._avg


    def aprovado( self ):
        """Aprovação."""
        media = self.avg
        if media is None:
            return False
        return self.avg.br_grade >= self.MEDIA_APROV


    def get_credits( self ) -> int:
        """Os creditos recebidos pela disciplina, 0 se reprovado."""
        return self.credit if self.aprovado() else 0
        

    def __repr__( self ):
        return "ClassGrades( '{nome}', prova1={prova1}, prova2={prova2}, credit={credit}, avg={_avg} )".format( **self.__dict__ ) 


_classes_list = [ ('logica matematica',        4),
                  ('engenharia de software',   6),
                  ('teoria da computacao',     3),
                  ('banco de dados',           6),
                  ('arquitetura de software',  4) ]





class Curso:
    """Junta todas as diciplinas do aluno."""

    def __init__( self, classes_list : List[ Tuple[ str, ClassGrades ]]=_classes_list ):
        # Gera dicionário de nomes->'objetos da disciplina'
        self._classes_list = classes_list
        self._all_classes = _all_classes = set( map( lambda cla_cred : ClassGrades( cla_cred[0], credit=cla_cred[1]),
                        self._classes_list ))
        self.classes_names = dict( map( lambda cla: ( cla.nome, cla ), self._all_classes ) )


    def pick_class( self, class_name ) -> ClassGrades:
        name = class_name.casefold()
        try:
            return self.classes_names[ name ]
        except:
            raise RuntimeError( f"Não existe registro da curso com nome {class_name}" )


    def out_media( self, class_name : str ) -> Grade:
        return self.pick_class( class_name ).avg

    def in_media( self, class_name : str, us_grade : str ) -> None:
        self.pick_class( class_name )._avg = GradeUs( us_grade )

    def in_prova1( self, class_name, us_grade : str ) -> None:
        self.pick_class( class_name ).prova1 = GradeUs( us_grade )

    def in_prova2( self, class_name, us_grade : str ) -> None:
        self.pick_class( class_name ).prova2 = GradeUs( us_grade )


    def out_creditos_ganhos( self ) -> int:
        tot = 0
        for cla in self._all_classes:
            # No exemplo matérias sem nota também são consideradas com créditos
            if cla.aprovado() or cla.avg is None:
                tot += cla.get_credits()
        return tot

    def out_reprovadas( self ) -> List[ str ]:
        """Nome de todas as classes reprovadas."""
        return list( map( lambda c: c.nome,
                          filter( lambda cla: not cla.aprovado(), self._all_classes ) ))

    def out_total_creditos( self ) -> int:
        """Total de creditos de todas as disciplinas."""
        tot = 0
        for c in self._all_classes:
            tot += c.credit
        return tot

    def out_ness_prova1( self, class_name : str, media_d=None ) -> Grade:
        """Qual a nota necessária na prova1 para passar."""
        
        cl = self.pick_class( class_name )

        if not media_d:
            media_d = cl.MEDIA_APROV
        else:
            media_d = media_d.br_grade

        if cl.prova1 is None and cl.prova2 is None:
            return None
        
        if not cl.prova2 is None:
            return Grade( media_d * 2 - cl.prova2.br_grade )

    def out_ness_prova2( self, class_name : str, media_d=None ) -> Grade:
        """Qual a nota nessesária na prova2 para passar."""
        cl = self.pick_class( class_name )

        if not media_d:
            media_d = cl.MEDIA_APROV
        else:
            media_d = media_d.br_grade

        if cl.prova1 is None and cl.prova2 is None:
            return None
        
        if not cl.prova1 is None:
            return Grade( media_d * 2 - cl.prova1.br_grade )

    def out_ness( self, class_name : str, media_d=None ):
        """Nota nessasária para passar."""
        cl = self.pick_class( class_name )

        if media_d is None:
            media_d = cl.MEDIA_APROV
        else:
            media_d = media_d.br_grade

        if cl.prova1 is None and cl.prova2 is None:
            return Grade( cl.MEDIA_APROV / 2), 'ambas'
        elif cl.prova1 is None:
            return self.out_ness_prova1( class_name, Grade( media_d )), 'prova1'
        elif cl.prova2 is None:
            return self.out_ness_prova2( class_name, Grade( media_d )), 'prova2'
        else:
            return None, 'feitas'








import unicodedata
def strip_accents( s : str ) -> str:
    """Remove os acentos e deixa minúscula."""
    return str().join( filter( lambda c: unicodedata.category( c ) != 'Mn',
                               unicodedata.normalize( 'NFD', s ))).casefold()



#######################################################################
# Testes
#######################################################################
import unittest


class TestStripAccents( unittest.TestCase ):
    def test_strip_accents( self ):
        self.assertEqual( strip_accents( 'áÁéÉíÍóÓúÚ' ), 'aaeeiioouu' )
        self.assertEqual( strip_accents( 'ÃõẽÇçáñóṕńÇçḉÔÛü' ), 'aoeccanopncccouu' )
        self.assertEqual( strip_accents( '~~.áééÇ' ), '~~.aeec' )


class TestCurso( unittest.TestCase ):
    def setUp( self ):
        self.c = Curso()

    def test_exemplo1( self ):
        c = self.c

        #entradas
        d = 'logica matematica'
        c.in_media( d, 'C' )
        self.assertEqual( c.pick_class( d ).avg.us_grade, 'c' )

        d = 'engenharia de software'
        c.in_prova1( d, 'A' )
        c.in_prova2( d, 'B' )
        self.assertEqual( c.pick_class( d ).prova1.us_grade, 'a' )
        self.assertEqual( c.pick_class( d ).prova2.us_grade, 'b' )

        d = 'banco de dados'
        c.in_media( d, 'B' )
        self.assertEqual( c.pick_class( d ).avg.us_grade, 'b' )

        d = 'teoria da computacao'
        c.in_prova1( d, 'F' )
        c.in_prova2( d, 'D' )
        self.assertEqual( c.pick_class( d ).prova1.us_grade, 'f' )
        self.assertEqual( c.pick_class( d ).prova2.us_grade, 'd' )

        #saídas
        d = 'logica matematica'
        self.assertEqual( c.out_media( d ).us_grade, 'c' )

        d = 'engenharia de software'
        self.assertTrue( c.pick_class( d ).aprovado() )
        self.assertEqual( c.out_media( d ).us_grade, 'b' )

        d = 'teoria da computacao'

        self.assertIn( 'teoria da computacao', c.out_reprovadas() )

        self.assertEqual( c.out_total_creditos(), 23 )


    def test_exemplo2( self ):
        c = self.c

        d = 'teoria da computacao'
        c.in_media( d, 'b' )
        self.assertEqual( c.pick_class( d ).avg.us_grade, 'b' )

        d = 'engenharia de software'
        c.in_prova1( d, 'c' )


        d = 'logica matematica'
        c.in_prova1( d, 'd' )

        d = 'banco de dados'
        c.in_prova1( d, 'c' )
        c.in_prova2( d, 'b' )

        d = 'arquitetura de software'
        c.in_prova1( d, 'b' )
        c.in_prova2( d, 'c' )

        #saída
        d = 'teoria da computacao'
        self.assertEqual( c.out_media( d ).us_grade, 'b' )

        d = 'engenharia de software'
        self.assertEqual( c.out_ness_prova2( d, GradeUs( 'b' )).us_grade, 'a' )

        d = 'arquitetura de software'
        self.assertEqual( c.pick_class( d ).avg.us_grade, 'c' )

        d = 'logica matematica'
        a,_ = c.out_ness( d )
        self.assertEqual( a.us_grade, 'b' )

        

class CursoRepl:
    def __init__( self ):
        self.c = Curso()

    def error_response( self ) -> str:
        return "Nem ideia do que isso significa!"

    def nota_br_ou_us( self, ns : str ) -> Grade:
        """Nota em qualquer valor."""
        if ns in list( 'abcdf' ):
            return GradeUs( ns )
        else:
            return Grade( int( ns ))

    def repl( self ):
        pass

    def read_line( self, line : str ) -> None:
        l = strip_accents( line ).strip()
        return l

    def print_hello_msg( self ) -> None:
        print( "Programa de notas." )

        print( "Disciplinas cadastradas: ", end='' )
        di_names = []
        for di in self.c._all_classes:
            di_names.append( di.nome.title())
        print( ', '.join( di_names ))

        print( 'Entre com o comando desejado ou "sair".' )


        


    def repl( self ) -> None:
        self.print_hello_msg()
        while True:
            cmd_line = self.read_line( input( '> ') )
            if cmd_line in ['sair', 'sai', 'tchau', 'fim', 'fecha', 'fechar']:
                print( 'Tchau, tchau!' )
                break
            pline = self.eval_line( cmd_line )
            if pline != '':
                print( pline )




    def eval_line( self, l : str ) -> str:
        def format_grade( g : Grade, def_t='br' ) -> str:
            if def_t == 'br' or def_t is None:
                return "{:.1f}".format( g.br_grade / 10 )
            elif def_t == 'us':
                return g.us_grade.upper()
            return ''

        def read_grade( s: str ):
            if s in 'abcdf':
                return GradeUs( s )
            else:
                return Grade( int( float( s ) * 10 ))
        
        disciplina = self.pick_disciplina( l )
        value = self.pick_value( l )
        question = self.question( l )
        param = self.pick_param( l )
        tipo = self.pick_tipo_nota( l )
        
        if not question:
            if disciplina and (not disciplina in ['todas', 'cursadas']) and value and param:
                try:
                    para = read_grade( param )
                except:
                    return self.error_response()
                
                if value == 'prova1':
                    self.c.in_prova1( disciplina, para.us_grade)
                elif value == 'prova2':
                    self.c.in_prova2( disciplina, para.us_grade)
                elif value == 'media':
                    self.c.in_media( disciplina, para.us_grade)
                else:
                    return self.error_response()
                return ''
            else:
               return self.error_response()

                
        else: #question-output
            if l[-1] == '?':
                l = l[0:-1]

            if value in ['media', 'prova1', 'prova2', 'preciso' ]:
                if not disciplina:
                    return self.error_response
            
            if value == 'media':
                #TODO: mostar mensagem caso não tenha ambas as notas
                
                media = format_grade( self.c.out_media( disciplina ) , tipo )
                return "A média em {} foi {}.".format( disciplina.title(), media )

            elif value == 'prova1':
                grade = self.c.pick_class( disciplina ).prova1
                if grade is None:
                    return "Não tenho a nota para Prova1 de {}".format( disciplina.title() )

                p = format_grade( grade, tipo )
                return "Tirei {} na Prova1 em {}.".format( p, disciplina.title() )
            elif value == 'prova2':
                grade = self.c.pick_class( disciplina ).prova2
                if grade is None:
                    return "Não tenho a nota para Prova2 de {}".format( disciplina.title() )

                p = format_grade( grade , tipo )
                return "Tirei {} na Prova2 em {}.".format( p, disciplina.title() )
            
            elif value == 'aprovado' or value == 'reprovado':
                if disciplina == 'todas' or disciplina is None:
                    repro = self.c.out_reprovadas()
                    if repro == []:
                        return "Fui aprovado em todas as disciplinas"
                    else:
                        repro = map( str.title, repro )
                        return "Reprovei em " + ', '.join( repro ) + '.'
                
                aprov = self.c.pick_class( disciplina ).aprovado()
                if aprov:
                    media = format_grade( self.c.out_media( disciplina ), tipo )
                    return "Foi aprovado em {} com média {}.".format( disciplina.title(), media )
                else:
                    return "Não fui aprovado em {}.".format( disciplina.title() )

            elif value == 'credito':
                #verifica se quer todos os créditos ou só os aprovados
                partial = False
                part_str = ['cursei', 'aprovad', 'concluido', 'conclui', 'cursado', 'curs' ]
                for s in part_str:
                    if s in l:
                        partial = True
                        break

                if partial:
                    cred = self.c.out_creditos_ganhos()
                    return "Concluí {} creditos.".format( cred )
                else:
                    cred = self.c.out_total_creditos()
                    return "{} creditos esse semestre.".format( cred )
                


            elif value == 'preciso':
                media = self.pick_any_param( l, 'media' )
                if media is None:
                    media_val = Grade( ClassGrades.MEDIA_APROV )
                else:
                    media_val = read_grade( media )

                ness, prov =  self.c.out_ness( disciplina, media_val )
                if prov == 'feitas':
                    return "Ambas as provas já feitas em {} com média {}.".format( disciplina.title(),
                                                                                   format_grade( self.c.out_media( disciplina )), tipo)
                elif prov == 'ambas':
                    return "Preciso de {} em ambas as provas de {}".format( format_grade( ness, tipo ), disciplina.title())
                else: #prova1 or prova2
                    return "Preciso de {} na {} de {}.".format( format_grade( ness, tipo ), prov.title(), disciplina.title())
                    
                return ''
###return 'Preciso ' + ness + ' ' + prov + ' ' + disciplina
            return self.error_response()
        
        

    def pack_command_info( self, line : str ) -> Dict:
        """Guarda todas as informações sobre o comando em um dicionário. Para testes."""
        l = strip_accents( line ).strip()

        dic = { 'disciplina'  : self.pick_disciplina( l ),
                'value'       : self.pick_value( l ),
                'question'    : self.question( l ),
                'param'       : self.pick_param( l ),
                'tipo'        : self.pick_tipo_nota( l ),
                }

        return dic


    def pick_disciplina( self, cmd_line : str ):
        """Identifica a disciplina selecionada no comando. Pode retornar 'todas', ou 'cursadas' também."""
        dis_names = self.c.classes_names.keys()
        for name in dis_names:
            if name in cmd_line:
                return name
        if 'todas' in cmd_line:
            return 'todas'
        if 'cursadas' in cmd_line:
            return 'cursadas'
        #não achou
        return None

    VALUES = [ 'preciso', 'precisa', 'deve', 'reprovado', 'necessito', 'necessario', 'tirar', 'media', 'credito', 'creditos', 'reprovei' 'nao passar', 'nao aprovado', 'aprovado', 'nao reprovado', 'nao passei', 'passei', 'passar', 'nota para passar', 'prova1', 'prova2', 'prova 1', 'prova 2',  ]
    SAME_VAL = [['prova1', 'prova 1'],
                ['prova2', 'prova 2'],
                ['aprovado', 'nao reprovado', 'passei'],
                ['reprovado', 'nao aprovado', 'nao passei', 'reprovei'],
                ['passar', 'nota para passar'],
                ['credito', 'creditos'],
                ['preciso', 'precisa', 'deve', 'necessito', 'necessario'],]

                
                
    def pick_value( self, cmd_line : str ):
        """Identifica o valor desejado no comando."""
        v = None
        for val in self.VALUES:
            if val in cmd_line:
                v = val
                break

        # sinônimos
        for sim_list in self.SAME_VAL:
            if v in sim_list:
                v = sim_list[0]
                break

        return v
    
    QUESTIONS = [ 'qual', 'quanto', 'quanta' ]
    
    def question( self, cmd_line : str ):
        """Tipo de pergunta. None se for uma entrada. True se terminar em '?' mas não tiver 'qual' ou 'quanto(a)'."""
        for q in self.QUESTIONS:
            if q in cmd_line:
                return q
        if cmd_line[-1] == '?':
            return True
        return False

    def pick_any_param( self, cmd_line : str, val : str ):
        """Pega qualquer valor de parâmetro. Primeiro valor após val."""

        #Pega primeira palavra depois do nome do valor
        try:
            ri = cmd_line.rindex( val )
            para = cmd_line[ ri + len(val) :].split()[0]
            return para
        except:
            return None


    def pick_param( self, cmd_line : str ):
        """Valor de entrada para prova e media. None caso não seja entrada ou não tenha valor especificado"""
        question = self.question( cmd_line)
        if question:
            return None
        val = self.pick_value( cmd_line )
        if not val:
            return None

        return self.pick_any_param( cmd_line, val )


    def pick_tipo_nota( self, l : str ):
        """Qual o tipo de nota desejado."""
        if 'brasil' in l:
            return 'br'
        elif 'americ' in l:
            return 'us'
        return None
        


        
msgs1_exemplo1 = [ 'logica matematica media c',
                   'engenharia de software prova1 a',
                   'engenharia de software prova2 b',
                   'banco de dados media b',
                   'teoria da computacao prova1 f',
                   'teoria da computacao prova2 d',
                   'qual a media em pontuacao brasileira de logica matematica?',
                   'voce foi aprovado em engenharia de software?',
                   'qual a media da disciplina de teoria da computacao?',
                   'voce foi aprovado em todas as disciplinas?',
                   'quantos creditos voce concluiu?',
                   'quantos creditos voce cursou neste semestre?' ]

mex1 = list( zip( range( len( msgs1_exemplo1)), msgs1_exemplo1 ))
msgs1_exemplo2 = [ 'teoria da computacao media b',
                   'engenharia de software prova1 c',
                   'logica matematica prova1 d',
                   'banco de dados prova1 c',
                   'banco de dados prova2 b',
                   'arquitetura de software media b',
                   'arquitetura de software prova1 c',
                   'qual a media em pontuacao brasileira em teoria da computacao?',
                   'para ficar com media b em engenharia de software qual deve ser a nota da prova2?',
                   'qual a nota da prova2 em arquitetura de software?',
                   'qual a nota em pontuacao brasileira preciso tirar em logica matematica para passar na disciplina?',
                   'qual a media em banco de dados?' ]
mex2 = list( zip( range( len( msgs1_exemplo2)), msgs1_exemplo2 ))
                   
                   

class TestCursoRepl( unittest.TestCase ):
    def setUp( self ):
        self._cc = CursoRepl()

                       

    def test_pick_discipl( self ):
        cc = self._cc
        self.assertEqual( cc.pick_disciplina( 'fasdfasf' ), None );
        self.assertEqual( cc.pick_disciplina( 'qual a media em logica matematica?' ), 'logica matematica' );
        self.assertEqual( cc.pick_disciplina( 'banco de dados prova1  C' ), 'banco de dados' );
        self.assertEqual( cc.pick_disciplina( 'qual nota para passar em arquitetura de software?' ), 'arquitetura de software' )
        self.assertEqual( cc.pick_disciplina( 'qual a media em pontuacao brasileira de logica matematica?') , 'logica matematica' )

    def test_pick_value( self ):
        cc = self._cc
        self.assertEqual( cc.pick_value( 'fadsfadsffds' ), None )
        self.assertEqual( cc.pick_value( 'qual a media em pontuacao brasileira de logica matematica?' ), 'media' )
        m = msgs1_exemplo1
        self.assertEqual( cc.pick_value( m[3] ), 'media' )
        self.assertEqual( cc.pick_value( m[10] ), 'credito' )
        self.assertEqual( cc.pick_value( m[9] ), 'aprovado' )

        self.assertEqual( cc.pick_value( 'qual a nota da prova1 em banco de dados?' ), 'prova1' )
        


def test_unit():
    unittest.main( exit=False )


    """
cc = CursoRepl()

### Big teste
## Guarda todas as mensagens em um dicionário para verificar
mm = msgs1_exemplo1.copy()
m2_copy = msgs1_exemplo2.copy()
mm = mm + m2_copy
dic_pack = {}
for m in mm:
    dic_pack[m] = cc.pack_command_info( m )

#pp( dic_pack )

# pp( dic_pack )
def print_exemplo1():
    for m in msgs1_exemplo1:
        p = cc.eval_line( cc.read_line( m ))
        if p != '':
            print( p )

def print_exemplo2():
    for m in msgs1_exemplo2:
        p = cc.eval_line( cc.read_line( m ))
        if p != '':
            print( p )

#print_exemplo1()

        

c = Curso()
c.in_prova1( 'banco de dados', 'c' )
c.in_prova2( 'banco de dados', 'b' )
c.in_prova1( 'teoria da computacao', 'f' )
c.in_prova2( 'teoria da computacao', 'a' )

try:
    a = int( 'a' )
except:
    a = 10
"""



cc = CursoRepl()
cc.repl()
