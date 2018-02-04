# Invoice generator

A simple app usefull for generate recurrent invoices for your customers.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

- python >= 3.6
- python-pip
- python-virtualenv
- chrome browser >= 64

### Installing

```bash
> export INVOICE_GENERATOR_HOME=/path/to/invoice_generator/dir
> virtualenv --python=python3.6  $INVOICE_GENERATOR_HOME/venv
> source $INVOICE_GENERATOR_HOME/venv/bin/activate
> pip install -r $INVOICE_GENERATOR_HOME/requirements.txt
```

Create an alias of symbolic link to your chrome installation and call it __chrome__

```bash
> ln -s /path/to/chrome/executable chrome
```

Create your customer settings file by modifying the provided example

```bash
> nano $INVOICE_GENERATOR_HOME/customers/customer.json
```

And then generate your first invoice

```bash
> python $INVOICE_GENERATOR_HOME/invoice_generator $INVOICE_GENERATOR_HOME/customers/customer.json 1
```

## Authors

* **Simone Pandolfi** - *Initial work* - [SimonGSR](https://github.com/simongsr)

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details
