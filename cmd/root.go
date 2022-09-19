/*
Copyright © 2022 hobbymarks ihobbymarks@gmail.com
*/
package cmd

import (
	"errors"
	"os"
	"path/filepath"

	log "github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

var version = "0.0.0"

var giatRecordPath string

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:     "giat",
	Version: version,
	Short:   "unify local GitRepoDirecotry name",
	Long: `A tool for changing local GitRepoDirectory name to GitRepoName@OrganizationName.
For example:
	ProjectDir ==> GitRepoName@OrganizationName
	GiatLocalDir ==> giat@hobbymarks
	...
`,
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func init() {
	homeDir, err := os.UserHomeDir()
	if err != nil {
		log.Fatal(err)
	}
	giatRecordPath = filepath.Join(homeDir, ".giat")
	if _, err := os.Lstat(giatRecordPath); errors.Is(err, os.ErrNotExist) {
		err := os.Mkdir(giatRecordPath, os.ModePerm)
		if err != nil {
			log.Fatal(err)
		}
	}
}
