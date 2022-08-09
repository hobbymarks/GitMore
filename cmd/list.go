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
		var roots []string

		if len(args) >= 1 {
			for _, arg := range args {
				_, err := os.Stat(arg)
				if err != nil {
					log.Warning(err)
				} else {
					roots = append(roots, arg)
				}
			}
		} else {
			roots = []string{"./"}
		}

		for _, root := range roots {
			dirs, err := Dirs(root)
			if err != nil {
				log.Error(err)
			} else {
				gitDirs, err := GitDirs(dirs)
				if err != nil {
					log.Error(err)
				} else {
					fmt.Println(gitDirs)
				}
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

func GitDirs(rootDirs []string) ([]string, error) {
	var gitDirs []string

	for _, d := range rootDirs {
		gpath := filepath.Join(d, ".git")
		if _, err := os.Stat(gpath); !os.IsNotExist(err) {
			abs, err := filepath.Abs(d)
			if err != nil {
				log.Error(err)
			} else {
				gitDirs = append(gitDirs, abs)
			}
		}
	}

	return gitDirs, nil
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
