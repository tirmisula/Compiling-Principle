# ---------
# lex
# ---------
import ply.lex as lex
from ply.lex import TOKEN

tokens = (
    'PRECODE',
    'BLANK',
    'SIMPLELINE',
    'NORMALLINE',
    'CHAR',
    'NEWLINE',
    'IMG',
    'LINK',
    'HREF',
    'MAIL',
    'QLINK',
    'CODE',
    'BOLD',
    'EM',
    'HLEFT',
    'QUOTE',
    'OLSIGN0',
    'ULSIGN0',
    'OLSIGN1',
    'ULSIGN1',
    'OLSIGN2',
    'ULSIGN2',
    'WORD',
    'SPACE',
    'ENDLINE'
    )

lineBeg = r'(?:(?<=\n)|^)';

@TOKEN(r'\\\W')
def t_CHAR(t) :
    t.value = t.value[1]
    return t

@TOKEN(lineBeg+r'```.*\n(.*\n)*?```.*\n')
def t_PRECODE(t) :
    strs = t.value.split('\n')
    out = ''
    for s in strs[1:len(strs)-2] :
        out += s + '\n'
    t.value = out
    return t

@TOKEN(r'(?<!`)`.+?[^\\]`')
def t_CODE(t) :
    t.value = t.value[1:len(t.value)-1]
    return t

t_BLANK = lineBeg+r'\s*\n'
t_SIMPLELINE = lineBeg+r'(-[ \t]*){3,}\n'
t_NEWLINE = r'[ ][ ]+(?=\n)'

@TOKEN(lineBeg+r'(\*[ \t]*){3,}\n')
def t_NORMALLINE(t) :
    return t

@TOKEN(r'\*\*(.+?)\*\*|__(.+?)__')
def t_BOLD(t) :
    t.value = t.value[2:len(t.value)-2]
    return t

@TOKEN(r'\*(.+?)\*|_(.+?)_')
def t_EM(t) :
    t.value = t.value[1:len(t.value)-1]
    return t

@TOKEN(r'!\[[^\]\n]*]')
def t_IMG(t) :
    t.value = t.value[2:len(t.value)-1]
    return t

@TOKEN(r'\[[^\]\n]*]')
def t_LINK(t) :
    t.value = t.value[2:len(t.value)-1]
    return t

@TOKEN(r'\([^)\n]*\)')
def t_HREF(t) :
    t.value = t.value[1:len(t.value)-1]
    return t

@TOKEN(r'<(\w|\.)+@\w+(\.\w+)+>')
def t_MAIL(t) :
    t.value = t.value[1:len(t.value)-1]
    return t

@TOKEN(r'<\w+://.*?>')
def t_QLINK(t) :
    t.value = t.value[1:len(t.value)-1]
    return t

@TOKEN(lineBeg+r'\#{1,9}[ \t]*')
def t_HLEFT(t) :
    count = 0
    for ch in t.value :
        if ch == '#' :
            count += 1
        else :
            break
    t.value = count
    return t

@TOKEN(lineBeg+r'[ \t]*>[ >\t]*')
def t_QUOTE(t) :
    count = 0
    for ch in t.value :
        if ch == '>' :
            count += 1
    t.value = count
    return t

t_OLSIGN0 = lineBeg+r'[ ]{0,3}\d\.[ \t]+'
t_ULSIGN0 = lineBeg+r'[ ]{0,3}[-+*][ \t]+(?=\w)'
t_OLSIGN1 = lineBeg+r'[ ]{4,7}\d\.[ \t]+'
t_ULSIGN1 = lineBeg+r'[ ]{4,7}[-+*][ \t]+(?=\w)'
t_OLSIGN2 = lineBeg+r'[ ]{8,11}\d\.[ \t]+'
t_ULSIGN2 = lineBeg+r'[ ]{8,11}[-+*][ \t]+(?=\w)'

t_WORD = r'\S+'
t_SPACE = r'[ \t]+'
t_ENDLINE = r'\n'

def t_error(t) :
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

if __name__ == '__main__' :
    filename = 'test.md'
    data = open(filename).read()
    lexer.input(data)
    tok = lexer.token()
    while tok :
        print(tok)
        tok = lexer.token()
    print("===End of Lex Tokens===")

# ---------
# yacc
# ---------
import ply.yacc as yacc

def p_body_article(p) :
    '''body : article'''
    p[0] = p[1]

def p_article_block(p) :
    '''article : block'''
    p[0] = p[1]

def p_article_append(p) :
    '''article : article block'''
    p[0] = p[1] + p[2]

def p_blocks(p) :
    '''block : pre
             | ul
             | ol
             | para
             | quote
             | hr
             | hx'''
    p[0] = p[1]

def p_block_blank(p) :
    '''block : block BLANK'''
    p[0] = p[1]

def p_pre(p) :
    '''pre : PRECODE'''
    p[0] = '<pre><code>'+p[1]+'</code></pre>'

def p_quote_first(p) :
    '''quote : qline'''
    p[0] = '<blockquote>'+p[1]+'</blockquote>'

def p_quote_append(p) :
    '''quote : quote qline
             | quote line'''
    p[0] = p[1][0:len(p[1])-13]+p[2]+'</blockquote>'

def p_qline(p) :
    '''qline : QUOTE line'''
    p[0] = p[2]

def p_hr(p) :
    '''hr : SIMPLELINE
          | NORMALLINE'''
    p[0] = '<hr/>'

def p_hx(p) :
    '''hx : HLEFT line'''
    p[0] = '<h'+str(p[1])+'>'+p[2]+'</h'+str(p[1])+'>'

def p_inlines(p) :
    '''inline : word
              | space
              | char
              | br
              | img
              | link
              | em
              | bold
              | code'''
    p[0] = p[1]

def p_word(p) :
    '''word : WORD'''
    p[0] = p[1]

def p_space(p) :
    '''space : SPACE'''
    p[0] = ' '

def p_char(p) :
    '''char : CHAR'''
    p[0] = p[1]

def p_br(p) :
    '''br : NEWLINE'''
    p[0] = '<br/>'

def p_img(p) :
    '''img : IMG HREF'''
    p[0] = '<img alt="'+p[1]+'" src="'+p[2]+'"/>'

def p_link_normal(p) :
    '''link : LINK HREF'''
    p[0] = '<a href="'+p[2]+'">'+p[1]+'</a>'

def p_link_quick(p) :
    '''link : QLINK'''
    p[0] = '<a href="'+p[1]+'">'+p[1]+'</a>'

def p_link_mail(p) :
    '''link : MAIL'''
    p[0] = '<a href="mailto:'+p[1]+'">'+p[1]+'</a>'

def p_em(p) :
    '''em : EM'''
    p[0] = '<em>'+p[1]+'</em>'

def p_bold(p) :
    '''bold : BOLD'''
    p[0] = '<strong>'+p[1]+'</strong>'

def p_code(p) :
    '''code : CODE'''
    p[0] = '<code>'+p[1]+'</code>'

def p_line_first(p) :
    '''line : inline ENDLINE'''
    p[0] = p[1]

def p_line_front(p) :
    '''line : inline line'''
    p[0] = p[1] + p[2]

def p_para_first(p) :
    '''para : line BLANK'''
    p[0] = '<p>'+p[1]+'</p>'

def p_para_front(p) :
    '''para : line para'''
    p[0] = '<p>'+p[1]+p[2][3:]

# ul0
def p_ul_fisrt(p) :
    '''ul : ulli'''
    p[0] = '<ul>'+p[1]+'</ul>'

def p_ul_front(p) :
    '''ul : ulli ul'''
    p[0] = '<ul>'+p[1]+p[2][4:]

def p_ulli_init(p) :
    '''ulli : ULSIGN0 line'''
    p[0] = '<li>'+p[2]+'</li>'

def p_ulli_subList(p) :
    '''ulli : ulli ul1
            | ulli ol1'''
    p[0] = p[1][0:len(p[1])-5] + p[2] + '</li>'

# ul1
def p_ul1_fisrt(p) :
    '''ul1 : ul1li'''
    p[0] = '<ul>'+p[1]+'</ul>'

def p_ul1_front(p) :
    '''ul1 : ul1li ul1'''
    p[0] = '<ul>'+p[1]+p[2][4:]

def p_ul1li_init(p) :
    '''ul1li : ULSIGN1 line'''
    p[0] = '<li>'+p[2]+'</li>'

def p_ul1li_subList(p) :
    '''ul1li : ul1li ul2
             | ul1li ol2'''
    p[0] = p[1][0:len(p[1])-5] + p[2] + '</li>'

# ul2
def p_ul2_fisrt(p) :
    '''ul2 : ul2li'''
    p[0] = '<ul>'+p[1]+'</ul>'

def p_ul2_front(p) :
    '''ul2 : ul2li ul2'''
    p[0] = '<ul>'+p[1]+p[2][4:]

def p_ul2li_init(p) :
    '''ul2li : ULSIGN2 line'''
    p[0] = '<li>'+p[2]+'</li>'

def p_error(p) : 
    if p :
        print(yacc.token())
    else:
        print("error at EOF")

# ol0
def p_ol_fisrt(p) :
    '''ol : olli'''
    p[0] = '<ol>'+p[1]+'</ol>'

def p_ol_front(p) :
    '''ol : olli ol'''
    p[0] = '<ol>'+p[1]+p[2][4:]

def p_olli_init(p) :
    '''olli : OLSIGN0 line'''
    p[0] = '<li>'+p[2]+'</li>'

def p_olli_subList(p) :
    '''olli : olli ol1
            | olli ul1'''
    p[0] = p[1][0:len(p[1])-5] + p[2] + '</li>'

# ol1
def p_ol1_fisrt(p) :
    '''ol1 : ol1li'''
    p[0] = '<ol>'+p[1]+'</ol>'

def p_ol1_front(p) :
    '''ol1 : ol1li ol1'''
    p[0] = '<ol>'+p[1]+p[2][4:]

def p_ol1li_init(p) :
    '''ol1li : OLSIGN1 line'''
    p[0] = '<li>'+p[2]+'</li>'

def p_ol1li_subList(p) :
    '''ol1li : ol1li ol2
            | ol1li ul2'''
    p[0] = p[1][0:len(p[1])-5] + p[2] + '</li>'

# ol2
def p_ol2_fisrt(p) :
    '''ol2 : ol2li'''
    p[0] = '<ol>'+p[1]+'</ol>'

def p_ol2_front(p) :
    '''ol2 : ol2li ol2'''
    p[0] = '<ol>'+p[1]+p[2][4:]

def p_ol2li_init(p) :
    '''ol2li : OLSIGN2 line'''
    p[0] = '<li>'+p[2]+'</li>'

parser = yacc.yacc()

if __name__ == '__main__' :
    filename = 'test.md'
    result = parser.parse(open(filename).read())
    open('test.html','w').write(result)
