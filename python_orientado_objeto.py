 #Aprende a como criar classes e objetos em Python pelo video abaixo:
 # https://www.youtube.com/watch?v=QAwNvlEd1aM
 #def nao sao funçoes sao metodos.

class Canal:
    #__init__ e um metodo construtor
    #self e uma referencia para o proprio objeto
    def __init__(self,nome, descricao, inscritos):
        self.nome = nome
        self.descricao = descricao
        self.inscritos = inscritos

    def inscrever(self, quantidade=1): #todo metodo tem que ter o self
        self.inscritos += quantidade

    def postar_video(self, video):
        if not hasattr(self, 'videos'): #verificando se o atributo videos existe
            self.videos = [] #criando o atributo videos
        self.videos.append(video) #adicionando o video a lista de videos

class canalEmpresarial(Canal): #herdando a classe Canal
    def __init__(self, nome, descricao, inscritos):
        super().__init__(nome, descricao, inscritos) #chamando o construtor da classe pai
        self._equipes = [] #atributo privado (_nomeatributo,nao pode ser acessado fora da classe)
    
    @property #serve pra tirar o parenteses do metodo
    def equipe(self):
        return self._equipes
    
    #metodo para adicionar membros a equipe
    def adicionar_menbro(self, membro):
        if membro not in self._equipes: #verificando se o membro ja esta na equipe
            self._equipes.append(membro)
        else:
            print(f"{membro} ja esta na equipe")

    def remover_membro(self, membro):
        if membro in self._equipes:
            self._equipes.remove(membro)
        else:
            print(f"{membro} nao esta na equipe")

class Video:
    def __init__(self, titulo, descricao):
        self.titulo = titulo
        self.descricao = descricao
        self.curtidas = 0
        self.descurtidas = 0
        self.visualizacoes = 0
        self.comentarios = []


    def __repr__(self):
        return f"<{self.titulo}>"

    def asistir(self):
        self.visualizacoes += 1

    def curtir(self):
        self.curtidas += 1

    def descurtir(self):
        self.descurtidas += 1
    
    def comentar(self, comentario):
        self.comentarios.append(comentario)

    def info(self):
        print(f"Titulo: {self.titulo}")
        print(f"Descricao: {self.descricao}")
        print(f"Curtidas: {self.curtidas}")
        print(f"Descurtidas: {self.descurtidas}")
        print(f"Visualizacoes: {self.visualizacoes}")
        print("Comentarios:")
        for comentario in self.comentarios:
            print(f"- {comentario}")
        print("\n")

    
class playlist:
    def __init__(self, nome):
         self.nome = nome
         self.videos = []

    def adicionar_video(self, video):
        if video not in self.videos:
            self.videos.append(video)
        else:
            print(f"{video} ja esta na playlist")

    def remover_video(self, video):
         if video in self.videos:
             self.videos.remove(video)
         else:
             print(f"{video} nao esta na playlist")
    def listar_videos(self):
            print(f"Playlist: {self.nome}")
            for video in self.videos:
                print(f"- {video.titulo}")   

#criando objetos da classe Canal
canal_pierre = Canal("Pierre","Melhores videos de programação", 1000)
canal_guanabara = Canal("Curso em video","Melhores videos de Python", 5000)
canal_duolingo = canalEmpresarial("Duolingo","Melhores videos de idiomas", 2000)

#imprimindo os atributos do objeto canal_pierre
#print(canal_pierre.nome)
#print(canal_guanabara.nome)


# #imprimindo a quantidade de inscritos do canal_pierre
### print(f"quantidade de inscritos do canal: {canal_pierre.inscritos}")
# #inscrevendo 100 pessoas no canal_pierre
# canal_pierre.inscrever(100)
### print(f"quantidade de inscritos do canal: {canal_pierre.inscritos}")


# print(f"membros do canal_duolingo: {canal_duolingo.equipe}")
# canal_duolingo.adicionar_menbro("Pierre")
# print(f"membros do canal_duolingo: {canal_duolingo.equipe}")
# canal_duolingo.adicionar_menbro("Ana")
# print(f"membros do canal_duolingo: {canal_duolingo.equipe}")
# canal_duolingo.adicionar_menbro("Pierre")
# print(f"membros do canal_duolingo: {canal_duolingo.equipe}")
# canal_duolingo.remover_membro("Ana")
# canal_duolingo.adicionar_menbro("Maria")
# print(f"membros do canal_duolingo: {canal_duolingo.equipe}")



Video_poo = Video("Python Objetos","Aprenda agora")
veido_discordpy = Video("Discord.py","Aprenda agora a criar um bot")

canal_pierre.postar_video(Video_poo)
canal_pierre.postar_video(veido_discordpy)
print(canal_pierre.videos)

playlist_programacao = playlist("Programação")
playlist_programacao.adicionar_video(Video_poo)
playlist_programacao.adicionar_video(veido_discordpy)
playlist_programacao.listar_videos()
