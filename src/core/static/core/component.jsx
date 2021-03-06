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
