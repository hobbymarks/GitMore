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
		results, err := AllGitDirs(args)
		if err != nil {
			log.Error(err)
		} else {
			for _, repo := range results {
				fmt.Println(repo)
			}
		}
	},
}

func init() {
	rootCmd.AddCommand(listCmd)
}

func AllGitDirs(rootPaths []string) ([]string, error) {
	var roots []string
	var results []string

	if len(rootPaths) >= 1 {
		for _, arg := range rootPaths {
			_, err := os.Stat(arg)
			if err != nil {
				log.Warning(err)
			} else {
				roots = append(roots, arg)
			}
		}
		//FIXME:should merge paths
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
				log.Trace(gitDirs)
				results = append(results, gitDirs...)
			}
		}
	}
	//TODO:support colorfull output
	//TODO:supoort output grouped,such as by directory or by arg ...
	return results, nil
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
			}).Error(err)
			return err
			//FIXME:should check error type,some error should ignore,such as permission ...
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
