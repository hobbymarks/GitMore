/*
Copyright © 2022 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"

	log "github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

// listCmd represents the list command
var listCmd = &cobra.Command{
	Use:   "list",
	Short: "list all git managed directory",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		rootPath := "./"
		if len(args) >= 1 {
			rootPath = args[0]
		}
		dirs, err := Dirs(rootPath)
		if err != nil {
			log.Fatal(err)
		}
		for _, d := range dirs {
			gitPath := filepath.Join(d, ".git")
			if _, err := os.Stat(gitPath); !os.IsNotExist(err) {
				fmt.Println(d)
			}
		}
	},
}

func init() {
	rootCmd.AddCommand(listCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// listCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// listCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}

func Dirs(rootPath string) ([]string, error) {
	var dirs []string
	rootPath = filepath.Clean(rootPath)
	log.Trace(rootPath)
	err := filepath.WalkDir(rootPath, func(path string, info fs.DirEntry, err error) error {
		if err != nil {
			log.WithFields(log.Fields{
				"Call": "filepath.WalkDir",
			}).Trace(err)
			return err
			//TODO:should check error type,some error should ignore,such as permission ...
		}
		if info.IsDir() {
			log.Trace("IsDir:", path)
			rel := path
			dirs = append(dirs, filepath.ToSlash(rel))
			return nil
		} else {
			log.Trace("Skipped:", path)
		}

		return nil
	})
	if err != nil {
		return nil, err
	}

	return dirs, nil
}
