import styled, {css} from 'styled-components';

export const Container = styled.div`
    display: flex;
    margin: 0 auto;
    flex-direction: column;
    align-items: center;
    padding-top: 20px;
`;

export const SectionLogon = styled.section`
    display: flex;
    flex-direction: column;
    input + input {
        margin-top: 10px;
        margin-bottom: 10px;
    }
`

export const Input = styled.input`
    padding: 5px;
    border-radius: 10px;
`;

export const Button = styled.button`
    padding: 5px;
    border-radius: 10px;
`;


export const SectionLogged = styled.section`
    display: flex;
    width: 20%;
    flex-direction: column;
    h2{
        margin-top: 25px;
    }
    button{
        margin-top: 10px;
    }
`

export const ContainerChat = styled.section`
    display: flex;
    flex-direction: row;
    width: 80%;
    height: max-content;
    margin-top: 20px;
    padding: 20px;
    background-color:var(--background-secondary-color) ;
    border-radius: 10px;
`

export const SectionChatList = styled.div`
    display: flex;
    width: 20%;
    height: 100%;
    overflow-y: auto;
    flex-direction: column;
    margin: 0 5px;

    h2 {
        margin: auto;
    }

`

export const UserListArea = styled.div`
    display: flex;
    flex-direction: column;
    height: 350px;
    overflow-y: auto;
    background-color: #FFF;
    padding: 5px;
    border-radius: 10px;

`

export const UserCard = styled.button`
    display: flex;
    flex-direction: column;
    width: 100%;
    height: auto;
    padding: 10px;
    color: #DDD;
    border-radius: 10px;
    background-color: var(--background-color);
    margin-bottom: 5px;
`



export const SectionChat = styled.div`
    display: flex;
    width: 80%;
    height: max-content;
    flex-direction: column;
`

export const ChatArea = styled.div`
    width: 100%;
    height: 300px;
    padding: 5px;
    background-color: #FFF;
    overflow-y: auto;
    div + div{
        margin-top:10px ;
    }
`;

interface IChatCard {
    isSelfMessage?: boolean;
}


export const ChatCard = styled.div<IChatCard>`
    display: flex;
    flex-direction: column;
    max-width: 50%;
    height: auto;
    padding: 10px;

    border-radius: 10px;
    background-color: var(--background-color);

      ${(props) =>
    props.isSelfMessage
      ? css`
          margin-left: auto;
        `
      : css`
          margin-right: auto;
        `}

    span{
        color: #DDD;
    }
`

export const ChatUser = styled.div`

    display: flex;
    flex-direction: column;
    width: 100%;

    margin-top: 10px;
    
`

export const TextAreaChat = styled.textarea`
    width: 100%;    
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
`
