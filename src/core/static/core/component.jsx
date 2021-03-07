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

class HorizontalNav extends React.Component {
  render() {
    if(!Array.isArray(this.props.children)) {
      // There is only one child, and React doesn't wrap it in a list
      return <nav className='horizontal'>{ this.props.children }</nav>;
    }
    let nonEmptyChildren = this.props.children.filter(child => child);
    let pseudoChildren = [];

    for(let i = 0; i < nonEmptyChildren.length; i++) {
      if(i > 0) {
        pseudoChildren.push('|');
      }
      pseudoChildren.push(nonEmptyChildren[i]);
    }

    return <nav className='horizontal'>{pseudoChildren}</nav>
  }
}

class Form extends React.Component {
  render() {
    let onFailure = this.props.onFailure || (r => {});
    let handleSubmit = e => {
      e.preventDefault();

      let form = e.target;

      let data = {};

      Object.keys(form.elements).forEach(key => {
        let element = form.elements[key];
        if (element.type === "submit") {
          // Do nothing
        } else if(element.type === 'checkbox') {
          data[element.name] = element.checked;
        } else {
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
          onFailure: onFailure,
          onSuccess: () => {
            this.props.onSuccess();
            Object.keys(form.elements).forEach(key => {
              e = form.elements[key];

              if(e.type !== 'submit') e.value = '';
            });
          }
        }
      );
    };

    return <form className={this.props.className} onSubmit={handleSubmit}>
      { this.props.children }
    </form>;
  }
}

class ModelDisplay extends React.Component {
  render() {
    let fields = this.props.fields;
    let instance = this.props.instance;

    const getHumanReadable = field => {
      return (field.charAt(0).toUpperCase() + field.slice(1)).split('_').join(' ');
    };

    let content = [];

    fields.forEach(field => {
      let value = instance[field] || '';
      let hr = getHumanReadable(field);

      content.push(<label key={field + '-label'} htmlFor={field + '-value'}>{hr}:</label>);
      content.push(<span key={field + '-value'}>{value}</span>);
    });

    return <div className='model-display'>
      { content }
    </div>;
  }
}

class ModelForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      errors: {}
    };
  }

  render() {
    let endpoint = this.props.endpoint;
    let fields = this.props.fields;
    let instance = this.props.instance || null;
    let onSave = this.props.onSave || (() => {});
    let onCancel = this.props.onCancel || (() => {});

    let requestMethod = null;
    let handler = null;

    if(instance) {
      requestMethod = 'PUT';
      handler = endpoint + instance.identifier + '/';
    } else {
      requestMethod = 'POST';
      handler = endpoint;
    }

    const getHumanReadable = field => {
      return (field.charAt(0).toUpperCase() + field.slice(1)).split('_').join(' ');
    };

    const createForm = () => {
      let result = [];

      fields.forEach(field => {
        let defaultValue = '';
        if(instance) {
          defaultValue = instance[field];
        }

        let hr = getHumanReadable(field);

        let fieldErrors = this.state.errors[field] || [];

        result.push(
          <label
              key={ field + '-label' }
              htmlFor={field + '-input'}>
            {hr}:
          </label>
        );
        result.push(
          <input
              key={ field + '-input' }
              defaultValue={defaultValue}
              name={field}
              placeholder={field}
              type='text'/>
        );
        result.push(<ul key={ field + '-errors' }>
          { fieldErrors.map((fe, i) => <li key={i} className='error'>{ fe }</li>) }
        </ul>);
      });

      return result;
    };

    const createNav = () => {
      if(instance) {
        return <HorizontalNav>
          <input type='submit' value='Save'></input>
          <button onClick={() => onCancel()}>Cancel</button>
        </HorizontalNav>;
      } else {
        return <HorizontalNav>
          <input type='submit' value='Create'></input>
        </HorizontalNav>;
      }
    };

    let handleSuccess = r => {
      this.setState({errors: {}});
      this.props.onSave();
    };

    return <Form
        className='model-form'
        csrf_token={this.props.csrf_token}
        requestMethod={requestMethod}
        handler={handler}
        onFailure={response=>this.setState({ errors: response })}
        onSuccess={handleSuccess}>
      <div className='fields'>{ createForm() }</div>
      { createNav() }
    </Form>;
  }
}

class ModelEditor extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      editing: false
    };
  }

  render() {
    let onEdit = this.props.onEdit || (() => {});
    let onDelete = this.props.onDelete || (() => {});

    if(this.state.editing) {
      let handleSave = () => {
        this.setState({editing: false});
        this.props.onEdit();
      };

      return <div className='model-editor'>
        <ModelForm
            csrf_token={this.props.csrf_token}
            endpoint={this.props.endpoint}
            fields={this.props.fields}
            instance={this.props.instance}
            onSave={handleSave}/>
      </div>;
    }

    let editButton = null;

    if(this.props.editable) {
      let handleEdit = () => this.setState({ editing: true });
      editButton = <button onClick={handleEdit}>Edit</button>;
    }

    let deleteButton = null;

    if(this.props.deletable) {
      let handleDelete = () => {
        delete_(
          this.props.endpoint + this.props.instance.identifier + '/',
          {
            headers: {
              'X-CSRFToken': this.props.csrf_token
            },
            onSuccess: onDelete
          }
        );
      };

      deleteButton = <DeleteButton onDelete={handleDelete}/>;
    }

    return <div className='model-editor'>
      <ModelDisplay
          fields={this.props.fields}
          instance={this.props.instance}/>
      <HorizontalNav>
        { this.props.extraNav }
        { editButton }
        { deleteButton }
      </HorizontalNav>
    </div>;
  }
}

ModelEditor.defaultProps = {
  extraNav: [],
  editable: true,
  deletable: true
};

class ModelManager extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      instanceList: null
    };
  }

  componentDidMount() {
    this.getInstanceList();
  }

  getInstanceList() {
    let endpoint = this.props.endpoint;
    get(endpoint, { onSuccess: r => this.setState({instanceList: r}) });
  }

  render() {
    if(this.state.instanceList === null) {
      return 'Loading...';
    }

    let endpoint = this.props.endpoint;
    let fields = this.props.fields;
    let getDeletable = this.props.getDeletable || (instance => true);
    let getEditable = this.props.getEditable || (instance => true);
    let getExtraNav = this.props.getExtraNav || ((instance, triggerManagerRefresh) => null);

    let handleChange = () => this.getInstanceList();

    let getEditor = instance => {
      return <ModelEditor
          key={instance.identifier}
          csrf_token={this.props.csrf_token}
          deletable={getDeletable(instance)}
          editable={getEditable(instance)}
          endpoint={endpoint}
          extraNav={getExtraNav(instance, handleChange)}
          fields={fields}
          instance={instance}
          onDelete={handleChange}
          onEdit={handleChange}/>;
    };

    return <div className='model-manager'>
      <ModelForm
        csrf_token={ this.props.csrf_token }
        endpoint={endpoint}
        fields={fields}
        onSave={handleChange}/>
      <div className='model-editor-list'>
        {this.state.instanceList.map(getEditor)}
      </div>
      <button onClick={() => this.props.onComplete()}>Done</button>
    </div>;
  }
}
