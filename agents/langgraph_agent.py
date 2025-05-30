from typing import Dict, Any, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph.message import add_messages

from core.models.conversation_models import ConversationState
from agents.nodes.conversation_nodes import (
    initialize_conversation_node,
    process_user_response_node,
    clarification_node,
    next_question_node,
    finalize_conversation_node,
    decision_node
)


class GraphState(TypedDict):
    """Estado compatible con LangGraph"""
    messages: Annotated[list[BaseMessage], add_messages]
    pending_questions: list[str]
    user_responses: dict[str, str]
    current_question: str
    current_question_index: int
    needs_clarification: bool
    clarification_reason: str
    conversation_complete: bool
    metadata: dict[str, Any]


def graph_to_conversation_state(graph_state: GraphState) -> ConversationState:
    """Convierte GraphState a ConversationState"""
    state = ConversationState()
    state.messages = graph_state.get("messages", [])
    state.pending_questions = graph_state.get("pending_questions", [])
    state.user_responses = graph_state.get("user_responses", {})
    state.current_question = graph_state.get("current_question")
    state.current_question_index = graph_state.get("current_question_index", 0)
    state.needs_clarification = graph_state.get("needs_clarification", False)
    state.clarification_reason = graph_state.get("clarification_reason")
    state.conversation_complete = graph_state.get("conversation_complete", False)
    state.metadata = graph_state.get("metadata", {})
    return state


def conversation_to_graph_state(conv_state: ConversationState) -> GraphState:
    """Convierte ConversationState a GraphState"""
    return GraphState(
        messages=conv_state.messages,
        pending_questions=conv_state.pending_questions,
        user_responses=conv_state.user_responses,
        current_question=conv_state.current_question or "",
        current_question_index=conv_state.current_question_index,
        needs_clarification=conv_state.needs_clarification,
        clarification_reason=conv_state.clarification_reason or "",
        conversation_complete=conv_state.conversation_complete,
        metadata=conv_state.metadata
    )


class AdaptieraRRHHAgent:
    """
    Agente conversacional de RRHH usando un ConversationState interno
    con procesamiento directo de nodos.
    
    Este agente maneja entrevistas automatizadas, recopila respuestas,
    decide cuándo repreguntar y envía resúmenes por correo.
    """
    
    def __init__(self):
        self.state = ConversationState()
        self.initialized = False
    
    def start_conversation(self) -> str:
        """
        Inicia una nueva conversación.
        
        Returns:
            Mensaje inicial del agente
        """
        try:
            print("🚀 Iniciando conversación...")
            
            # Inicializar estado
            self.state = initialize_conversation_node(self.state)
            self.initialized = True
            
            # Retornar el último mensaje del agente
            if self.state.messages:
                ai_messages = [msg for msg in self.state.messages if isinstance(msg, AIMessage)]
                if ai_messages:
                    return ai_messages[-1].content
            
        except Exception as e:
            print(f"Error al iniciar conversación: {e}")
            return "Lo siento, hubo un error al iniciar la conversación. ¿Puedes intentar de nuevo?"
        
        return "¡Hola! Soy el asistente de RRHH. ¿Cómo puedo ayudarte?"
    
    def process_user_input(self, user_input: str) -> str:
        """
        Procesa la entrada del usuario y retorna la respuesta del agente.
        
        Args:
            user_input: Mensaje del usuario
            
        Returns:
            Respuesta del agente
        """
        # Si no está inicializado, inicializar primero
        if not self.initialized:
            initial_response = self.start_conversation()
            # Después procesar el input
            
        try:
            # Agregar mensaje del usuario
            user_message = HumanMessage(content=user_input)
            self.state.messages.append(user_message)
            
            # Procesar según el estado actual
            while True:
                decision = decision_node(self.state)
                print(f"Decisión tomada: {decision}")
                
                if decision == "process_response":
                    self.state = process_user_response_node(self.state)
                elif decision == "clarify":
                    self.state = clarification_node(self.state)
                    break  # Esperamos respuesta del usuario
                elif decision == "next_question":
                    self.state = next_question_node(self.state)
                    break  # Esperamos respuesta del usuario o terminamos
                elif decision == "finalize":
                    self.state = finalize_conversation_node(self.state)
                    break  # Conversación terminada
                elif decision == "wait_for_user":
                    break  # Esperamos respuesta del usuario
                else:
                    print(f"⚠️ Decisión desconocida: {decision}")
                    break
            
            # Retornar el último mensaje del agente
            if self.state.messages:
                # Buscar el último mensaje del agente después del input del usuario
                user_message_found = False
                for i in range(len(self.state.messages) - 1, -1, -1):
                    msg = self.state.messages[i]
                    if isinstance(msg, HumanMessage) and msg.content == user_input:
                        user_message_found = True
                        continue
                    if user_message_found and isinstance(msg, AIMessage):
                        return msg.content
                
                # Fallback: último mensaje del agente
                ai_messages = [msg for msg in self.state.messages if isinstance(msg, AIMessage)]
                if ai_messages:
                    return ai_messages[-1].content
            
        except Exception as e:
            print(f"Error al procesar input del usuario: {e}")
            import traceback
            traceback.print_exc()
            return "Lo siento, hubo un problema procesando tu respuesta. ¿Puedes intentar de nuevo?"
        
        return "Lo siento, no pude procesar tu respuesta. ¿Puedes intentar de nuevo?"
    
    def is_conversation_complete(self) -> bool:
        """
        Verifica si la conversación ha terminado.
        
        Returns:
            True si la conversación está completa
        """
        return self.state.conversation_complete
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de la conversación.
        
        Returns:
            Diccionario con el resumen de la conversación
        """
        return {
            "responses": self.state.user_responses,
            "questions_asked": len(self.state.user_responses),
            "total_questions": len(self.state.pending_questions),
            "complete": self.state.conversation_complete,
            "messages_count": len(self.state.messages)
        }
    
    def reset_conversation(self):
        """Reinicia la conversación"""
        self.state = ConversationState()
        self.initialized = False


# Función de conveniencia para crear una instancia del agente
def create_rrhh_agent() -> AdaptieraRRHHAgent:
    """
    Crea una nueva instancia del agente de RRHH.
    
    Returns:
        Instancia del agente configurada
    """
    return AdaptieraRRHHAgent() 