package migrations

func alreadyexists(err error) bool{
	return err != nil && err.Error() == "(NamespaceExists) Collection already exists"
}