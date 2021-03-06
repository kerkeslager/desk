class DeleteButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isConfirming: false
    };
  }

  render() {
    if(this.state.isConfirming) {
      return <span className='delete-button'>
        Are you sure?
        <button onClick={() => this.props.onDelete()}>Delete</button>
        |
        <button onClick={() => this.setState({ isConfirming: false})}>Cancel</button>
      </span>;
    }

    return <button onClick={() => this.setState({ isConfirming: true})}>
      Delete
    </button>;
  }
}

class Form extends React.Component {
  render() {
    let handleSubmit = e => {
      e.preventDefault();

      let form = e.target;

      let data = {};

      Object.keys(form.elements).forEach(key => {
        let element = form.elements[key];
        if (element.type !== "submit") {
          data[element.name] = element.value;
        }
      });

      request(
        this.props.requestMethod,
        this.props.handler,
        {
          data: data,
          headers: {
            'X-CSRFToken': this.props.csrf_token
          },
          onSuccess: this.props.onSuccess
        }
      );
    };

    return <form onSubmit={handleSubmit}>
      { this.props.children }
    </form>;
  }
}
